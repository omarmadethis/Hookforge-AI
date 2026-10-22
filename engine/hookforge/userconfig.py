"""Per-user config loader. Real, owner-specific files (config/<name>.json) are gitignored; the repo ships
config/<name>.example.json with placeholders. Every module reads config through cfg_path()/load() so a fresh
clone works on the example files and an owner's local files override them."""
import json, os
from .config import REPO

CONFIG_DIR = os.path.join(REPO, "config")

def cfg_path(name):
    """config/<name>.json if the owner created it, else config/<name>.example.json."""
    real = os.path.join(CONFIG_DIR, f"{name}.json")
    return real if os.path.exists(real) else os.path.join(CONFIG_DIR, f"{name}.example.json")

def load(name, default=None):
    p = cfg_path(name)
    if not os.path.exists(p):
        if default is not None: return default
        raise FileNotFoundError(f"missing {p}: copy config/{name}.example.json to config/{name}.json and fill it in")
    return json.load(open(p))

def using_example(name):
    return cfg_path(name).endswith(".example.json")
