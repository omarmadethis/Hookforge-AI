"""D44d - the ONLY way a file may leave the box (Drive upload, CopyFromBox, attachments).

    from hookforge import deliver
    staged = deliver.stage(path, name)   # scan -> refuse (raises Refused) or copy into OUT_DIR
    # then upload ONLY `staged` (UploadFile sourcePath must be inside deliver.OUT_DIR)
    deliver.verify_staged(staged)       # re-check right before upload (hash + rescan)

Whitelist policy, no override flag: any metadata field outside ALLOWED, any box outside the
allowed MP4 tree, any PNG chunk / JPEG segment outside the allowed set, or any trace string in the bytes
means a hard refusal. sanitize() makes clean copies (lossless when possible), and they must pass scan() too."""
import hashlib, json, os, re, shutil, struct, subprocess

OUT_DIR = "/workspace/hookforge/out/deliver"
MANIFEST = os.path.join(OUT_DIR, "manifest.json")

class Refused(Exception): pass

# ---- whitelist of exiftool fields (group:tag). System/File/ExifTool/Composite are about the filesystem or derived values. ----
ALWAYS_GROUPS = {"System", "File", "ExifTool", "Composite"}
QT_OK = {"CompatibleBrands","CreateDate","CurrentTime","Duration","HandlerType","HandlerVendorID","MajorBrand","MatrixStructure",
         "MediaDataOffset","MediaDataSize","MinorVersion","ModifyDate","MovieHeaderVersion","NextTrackID","PosterTime","PreferredRate",
         "PreferredVolume","PreviewDuration","PreviewTime","SelectionDuration","SelectionTime","TimeScale"}
TRACK_OK = {"AverageBitrate","BitDepth","BufferSize","ColorPrimaries","ColorProfiles","CompressorID","GraphicsMode","HandlerDescription",
            "HandlerType","ImageHeight","ImageWidth","MatrixCoefficients","MatrixStructure","MaxBitrate","MediaCreateDate","MediaDuration",
            "MediaHeaderVersion","MediaLanguageCode","MediaModifyDate","MediaTimeScale","OpColor","PixelAspectRatio","SourceImageHeight",
            "SourceImageWidth","TrackCreateDate","TrackDuration","TrackHeaderVersion","TrackID","TrackLayer","TrackModifyDate","TrackVolume",
            "TransferCharacteristics","VideoFieldOrder","VideoFrameRate","VideoFullRangeFlag","XResolution","YResolution",
            "AudioBitsPerSample","AudioChannels","AudioFormat","AudioSampleRate","Balance"}
PNG_OK = {"ImageWidth","ImageHeight","BitDepth","ColorType","Compression","Filter","Interlace","SRGBRendering","Gamma",
          "PixelsPerUnitX","PixelsPerUnitY","PixelUnits","Palette","Transparency"}
JPEG_OK = {"JFIFVersion","ResolutionUnit","XResolution","YResolution","ThumbnailWidth","ThumbnailHeight"}
ALLOWED_HANDLER_VALUES = {"HandlerDescription": {"VideoHandler","SoundHandler"}, "HandlerVendorID": {"Apple"}}

TRACE = re.compile(rb"c2pa|jumb|jumd|Lavf|Lavc|libx26[45]|x26[45] \(build|x264 - core|ffmpeg|FFmpeg|Higgsfield|higgsfield|Seedance|seedance|"
                   rb"OpenAI|openai|DALL-?E|Midjourney|Stable ?Diffusion|Kling|Runway|Sora|Imagen|trainedAlgorithmicMedia|"
                   rb"DigitalSourceType|<x:xmpmeta|xmlns:xmp|photoshop:|Adobe|Hf-job|hf_job|grok|Grok|ChatGPT|GPT-[0-9]")
# Inside compressed media data, a 4-letter word turns up by chance (e.g. "grok" once in 45 MB), so only specific
# multi-token signatures are searched there: encoder SEI banners, Lavc version strings, C2PA/JUMBF labels, brand names of 6+ chars.
PAYLOAD_TRACE = re.compile(rb"Lavf\d+\.\d+|Lavc\d+\.\d+|libx26[45]|x26[45] \(build|x264 - core|ffmpeg|FFmpeg|Higgsfield|higgsfield|"
                           rb"Seedance|seedance|OpenAI|Midjourney|c2pa\.|urn:c2pa|jumdc2pa|<x:xmpmeta|trainedAlgorithmicMedia|ChatGPT")

def _split_mdat(b):
    """(everything except mdat payloads, concatenated mdat payloads). Non-MP4 files: all bytes are 'header'."""
    if b[4:8] != b"ftyp": return b, b""
    hdr, pay, s = [], [], 0
    while s + 8 <= len(b):
        sz, t = struct.unpack(">I4s", b[s:s+8]); h = 8
        if sz == 1: sz = struct.unpack(">Q", b[s+8:s+16])[0]; h = 16
        if sz == 0: sz = len(b) - s
        if sz < 8: hdr.append(b[s:]); break
        (pay if t == b"mdat" else hdr).append(b[s+h:s+sz] if t == b"mdat" else b[s:s+sz]); s += sz
    return b"".join(hdr), b"".join(pay)

# short tokens are too common in compressed bytes; they are checked only in metadata VALUES
VALUE_TRACE = re.compile(r"\bAI\b|\bGPT\b|\bVeo\b|\bxAI\b|generat|encoder|software|creator|made with|synth", re.I)

MP4_TOP = {"ftyp", "moov", "mdat", "free"}
MP4_TREE = {"moov": {"mvhd","trak","udta"}, "trak": {"tkhd","edts","mdia"}, "edts": {"elst"}, "mdia": {"mdhd","hdlr","minf"},
            "minf": {"vmhd","smhd","dinf","stbl"}, "dinf": {"dref"},
            "stbl": {"stsd","stts","stss","sdtp","ctts","stsc","stsz","stco","co64","sgpd","sbgp"}, "udta": {"meta"}, "meta": {"hdlr","ilst"}}
PNG_CHUNKS = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"sRGB", b"gAMA", b"pHYs"}
JPEG_SEGS = {0xC0,0xC1,0xC2,0xC4,0xDB,0xDD,0xDA,0xE0} | set(range(0xD0, 0xD8))   # SOF/DHT/DQT/DRI/SOS/APP0(JFIF)/RST

RIFF_OK = {"ImageWidth","ImageHeight","AlphaIsUsed","VP8Version","HorizontalScale","VerticalScale","WebP_Flags","BackgroundColor","AnimationLoopCount"}
WEBP_CHUNKS = {b"VP8 ", b"VP8L", b"VP8X", b"ALPH", b"ANIM", b"ANMF"}
C2PA_UUID = bytes.fromhex("d8fec3d61b0e483c92975828877ec481")   # ISO BMFF C2PA manifest box uuid

def c2pa_manifests(path):
    """D99/F96: structural C2PA/JUMBF detection per container. [] = none found."""
    b = open(path, "rb").read(); found = []
    if b[:2] == b"\xff\xd8":                                            # JPEG: APP11 (FFEB) JUMBF boxes
        i = 2
        while i + 4 <= len(b) and b[i] == 0xFF:
            m = b[i+1]
            if m in (0xD9, 0xDA): break
            n = struct.unpack(">H", b[i+2:i+4])[0]
            if m == 0xEB and (b"jumb" in b[i:i+2+n] or b"JP" == b[i+4:i+6]): found.append("JPEG APP11 JUMBF segment")
            i += 2 + n
    elif b[:8] == b"\x89PNG\r\n\x1a\n":                                 # PNG: caBX chunk
        i = 8
        while i + 8 <= len(b):
            n, t = struct.unpack(">I4s", b[i:i+8])
            if t == b"caBX" or (t in (b"iTXt", b"tEXt", b"zTXt") and b"c2pa" in b[i+8:i+8+n].lower()): found.append(f"PNG {t.decode('latin1')} C2PA chunk")
            i += 12 + n
    elif b[:4] == b"RIFF" and b[8:12] == b"WEBP":                         # WebP: C2PA RIFF chunk
        i = 12
        while i + 8 <= len(b):
            t = b[i:i+4]; n = struct.unpack("<I", b[i+4:i+8])[0]
            if t == b"C2PA" or (t in (b"XMP ", b"EXIF") and b"c2pa" in b[i+8:i+8+n].lower()): found.append(f"WebP {t.decode('latin1').strip()} C2PA chunk")
            i += 8 + n + (n & 1)
    elif b[4:8] == b"ftyp":                                               # MP4: top-level uuid box with the C2PA uuid / jumb box
        s = 0
        while s + 8 <= len(b):
            sz, t = struct.unpack(">I4s", b[s:s+8]); h = 8
            if sz == 1: sz = struct.unpack(">Q", b[s+8:s+16])[0]; h = 16
            if sz == 0: sz = len(b) - s
            if sz < 8: break
            if (t == b"uuid" and b[s+h:s+h+16] == C2PA_UUID) or t == b"jumb": found.append(f"MP4 {t.decode()} C2PA box")
            s += sz
    hdr, _ = _split_mdat(b)
    if re.search(rb"jumdc2pa|urn:c2pa|c2pa\.claim|c2pa\.manifest", hdr) and not found: found.append("C2PA label bytes")
    return found

def _webp_chunks(b, probs):
    if not (b[:4] == b"RIFF" and b[8:12] == b"WEBP"): probs.append("not a WebP"); return
    i = 12
    while i + 8 <= len(b):
        t = b[i:i+4]; n = struct.unpack("<I", b[i+4:i+8])[0]
        if t not in WEBP_CHUNKS: probs.append(f"WebP chunk {t.decode('latin1')} not allowed")
        i += 8 + n + (n & 1)

def _exif(path):
    out = subprocess.run(["exiftool","-a","-G1","-ee","-j","-s",path],capture_output=True,text=True,check=True).stdout
    return json.loads(out)[0]

def _mp4_boxes(b, s, e, parent, probs, path=""):
    while s + 8 <= e:
        sz, t = struct.unpack(">I4s", b[s:s+8]); h = 8
        if sz == 1: sz = struct.unpack(">Q", b[s+8:s+16])[0]; h = 16
        if sz == 0: sz = e - s
        if sz < 8: probs.append(f"bad box size at {s}"); return
        t = t.decode("latin1"); p = f"{path}/{t}"
        allowed = MP4_TOP if parent is None else MP4_TREE.get(parent, set())
        if t not in allowed: probs.append(f"box {p} not allowed")
        if t == "ilst" and sz > 8: probs.append(f"box {p} has item-list metadata ({sz} B)")
        if t == "hdlr" and parent == "meta" and b[s+h+8:s+h+12] != b"mdir": probs.append(f"udta meta handler {b[s+h+8:s+h+12]!r} not mdir/Apple")
        if t in MP4_TREE and t in allowed:
            _mp4_boxes(b, s+h+(4 if t == "meta" else 0), s+sz, t, probs, p)
        s += sz

def _png_chunks(b, probs):
    if b[:8] != b"\x89PNG\r\n\x1a\n": probs.append("not a PNG"); return
    i = 8
    while i + 8 <= len(b):
        n, t = struct.unpack(">I4s", b[i:i+8])
        if t not in PNG_CHUNKS: probs.append(f"PNG chunk {t.decode('latin1')} not allowed")
        i += 12 + n

def _jpeg_segs(b, probs):
    if b[:2] != b"\xff\xd8": probs.append("not a JPEG"); return
    i = 2
    while i + 4 <= len(b):
        if b[i] != 0xFF: probs.append(f"bad JPEG marker at {i}"); return
        m = b[i+1]
        if m == 0xD9: return
        if m not in JPEG_SEGS: probs.append(f"JPEG segment FF{m:02X} not allowed")
        if m == 0xE0 and b[i+4:i+9] != b"JFIF\x00": probs.append("APP0 is not plain JFIF")
        n = struct.unpack(">H", b[i+2:i+4])[0]
        if m == 0xDA:   # entropy-coded data until EOI: skip to the end
            return
        i += 2 + n

def scan(path):
    """Return list of problems ([] = clean). Never raises for content."""
    probs = []; b = open(path, "rb").read(); ext = os.path.splitext(path)[1].lower()
    hdr, payload = _split_mdat(b)
    for m in set(TRACE.findall(hdr)): probs.append(f"trace bytes {m!r}")
    for m in set(PAYLOAD_TRACE.findall(payload)): probs.append(f"trace bytes in media data {m!r}")
    if ext not in (".txt", ".md", ".csv", ".json", ".srt"):
        probs += [f"C2PA manifest: {m}" for m in c2pa_manifests(path)]   # D99/F96 hard block, before anything can return
    if ext in (".txt", ".md", ".csv", ".json", ".srt"):
        return probs                                          # text deliverables: byte scan only (captions may mention words)
    try: meta = _exif(path)
    except Exception as e: return probs + [f"exiftool failed: {e}"]
    kind = (meta.get("File:FileType") or "").upper()
    for k, v in meta.items():
        if k == "SourceFile": continue
        g, _, tag = k.partition(":")
        sv = str(v)
        if g in ALWAYS_GROUPS:
            if g == "Composite" or g == "System" or g == "ExifTool": continue
            if g == "File" and tag in {"FileType","FileTypeExtension","MIMEType","ImageWidth","ImageHeight","EncodingProcess",
                                       "BitsPerSample","ColorComponents","YCbCrSubSampling","Comment"}:
                if tag == "Comment": probs.append(f"JPEG comment: {sv[:60]}")
                continue
            probs.append(f"{k} not whitelisted"); continue
        ok = (g == "QuickTime" and tag in QT_OK) or (re.fullmatch(r"Track\d+", g) and tag in TRACK_OK) or \
             (g == "PNG" and tag in PNG_OK) or (g == "JFIF" and tag in JPEG_OK) or (g == "RIFF" and tag in RIFF_OK)
        if not ok: probs.append(f"{k}={sv[:60]} not whitelisted"); continue
        if tag in ALLOWED_HANDLER_VALUES and sv not in ALLOWED_HANDLER_VALUES[tag]: probs.append(f"{k}={sv} unexpected value")
        if VALUE_TRACE.search(sv) and tag not in ("HandlerDescription",): probs.append(f"{k}={sv[:60]} looks like a tool tag")
    if kind in ("MP4", "MOV", "M4A", "M4V"): _mp4_boxes(b, 0, len(b), None, probs)
    elif kind == "PNG": _png_chunks(b, probs)
    elif kind == "JPEG": _jpeg_segs(b, probs)
    elif kind.startswith("WEBP"): _webp_chunks(b, probs)
    elif ext not in (".txt",): probs.append(f"file type {kind or ext} has no whitelist - refuse")
    return sorted(set(probs))

# ---- sanitizers (produce candidates; still have to pass scan) ----
def _blank_sei_strings(path):
    """x265/x264 write their version+options as a user-data SEI inside hvcC/avcC (and keyframes). Overwrite the text
    with spaces in place: same length, no emulation-prevention change, so decoders ignore it. Lossless."""
    b = bytearray(open(path, "rb").read()); n = 0
    for m in list(re.finditer(rb"x26[45] \(build|x264 - core|Lavc\d+\.\d+\.\d+", b)):
        e = m.end() if m.group().startswith(b"Lavc") else b.find(b"\x00", m.start()); e = e if e > 0 else m.start() + 64
        b[m.start():e] = b" " * (e - m.start()); n += 1
    if n: open(path, "wb").write(bytes(b))
    return n

def sanitize(src, dst):
    ext = os.path.splitext(src)[1].lower()
    if ext in (".mp4", ".mov", ".m4v"):
        from hookforge import autoedit
        autoedit.clean_remux(src, dst); _blank_sei_strings(dst)
    elif ext == ".png":
        from PIL import Image
        im = Image.open(src); im.load(); clean = Image.new(im.mode, im.size); clean.putdata(list(im.getdata())) if im.mode == "P" else None
        c = im.convert("RGBA" if "A" in im.mode else "RGB"); c = Image.frombytes(c.mode, c.size, c.tobytes())   # D84: fresh image, no info/ICC carried over
        c.save(dst, "PNG", optimize=True)   # PIL writes only IHDR/IDAT/IEND
    elif ext in (".jpg", ".jpeg"):
        from PIL import Image
        Image.fromarray(__import__("numpy").array(Image.open(src).convert("RGB"))).save(dst, "JPEG", quality=95)   # PIL: SOI/APP0 JFIF/DQT/SOF/DHT/SOS only
    elif ext == ".webp":
        from PIL import Image
        im = Image.open(src); im.load(); c = im.convert("RGBA" if "A" in im.mode else "RGB"); c = Image.frombytes(c.mode, c.size, c.tobytes())
        c.save(dst, "WEBP", lossless=True)   # VP8L only, no EXIF/XMP/ICC/C2PA chunks
    else:
        shutil.copyfile(src, dst)
    return dst

def _sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()

def stage(path, name=None, auto_sanitize=True):
    """Scan, refuse or stage. The returned path in OUT_DIR is the only thing allowed to be uploaded/copied out."""
    os.makedirs(OUT_DIR, exist_ok=True); name = name or os.path.basename(path)
    dst = os.path.join(OUT_DIR, name)
    probs = scan(path)
    if probs and auto_sanitize:
        sanitize(path, dst + ".tmp" + os.path.splitext(path)[1]); os.replace(dst + ".tmp" + os.path.splitext(path)[1], dst)
        probs = scan(dst)
        if probs: os.remove(dst)
    elif not probs: shutil.copyfile(path, dst)
    if probs: raise Refused(f"{path}: " + "; ".join(probs))
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    man[name] = dict(src=path, sha256=_sha(dst)); json.dump(man, open(MANIFEST, "w"), indent=1)
    return dst

def verify_staged(staged):
    """Call right before an upload: must be in OUT_DIR, unchanged since staging, and still clean."""
    staged = os.path.abspath(staged)
    if os.path.dirname(staged) != OUT_DIR: raise Refused(f"{staged} is not in {OUT_DIR} - run deliver.stage first")
    man = json.load(open(MANIFEST)); rec = man.get(os.path.basename(staged))
    if not rec or rec["sha256"] != _sha(staged): raise Refused(f"{staged} changed since staging or was never staged")
    p = scan(staged)
    if p: raise Refused("; ".join(p))
    return True

PREVIEW_PREFIX = "preview__"
def preview(path, name=None):
    """D99/F96: the ONLY way a generated image/video (incl. a draft shown in chat) leaves the engine. Strips (sanitize),
    then hard-verifies: zero metadata whitelist scan, AI/tool tags, and no C2PA/JUMBF manifest in JPG/PNG/WebP/MP4.
    Returns the staged, verified path (in OUT_DIR, manifest-tracked) or raises Refused."""
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".m4v"): raise Refused(f"{path}: preview supports images/videos only")
    out = stage(path, PREVIEW_PREFIX + (name or os.path.basename(path)), auto_sanitize=True)
    verify_staged(out)
    if c2pa_manifests(out): os.remove(out); raise Refused(f"{out}: C2PA manifest survived the strip")
    return out

if __name__ == "__main__":   # python3 -m hookforge.deliver <file> [name]  -> prints staged path or exits 2
    import sys
    try: print(stage(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
    except Refused as e: print("REFUSED:", e); sys.exit(2)
