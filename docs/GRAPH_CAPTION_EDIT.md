# Graph API caption edit (D107) - approval-gated, token never stored

Used when a published FB reel hits the swap trigger (40K views or +10K in one hour) and Omar approves the new caption.
Buffer can only edit posts still in Buffer, so published reels go through Meta Graph API.

1. `fb_caption.queue_swap(candidate)` → item in learning/publish_queue/caption_swaps/ (AWAITING_OMAR_APPROVAL).
2. Omar approves in chat → `publish.approve_swap(id, "Omar", "<his words>")` (binds the exact text).
3. Review: `graph_caption.plan(id, video_id)` shows the POST (token redacted).
4. **Secure-form step:** Omar enters a **Page access token** for that Page in the Secure Form. Needed permissions:
   `pages_manage_posts`, `pages_read_engagement` (Page token from Graph API Explorer or the app's Page token flow,
   for the Page that owns the reel). The agent puts it in the process env `META_PAGE_TOKEN` for this one run only.
   It is never written to a file, chat, log or the swap item; error messages redact it.
5. `graph_caption.execute(id, video_id)`: GET (ownership + live caption must still equal the approved-against caption)
   → `POST /{video-id}` `description=<approved text>` → GET verify → `publish.mark_swapped`.
6. Unset `META_PAGE_TOKEN` afterwards. Without a token the call refuses; until then Omar can paste the new caption
   in Meta Business Suite and the agent records `mark_swapped(id, "manual")`.
