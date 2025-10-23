import os, datetime, pytz
from pathlib import Path
from PIL import Image
import imagehash

from bot.captions import build_caption, choose_variant
from bot.capture_trending import capture_trending
from bot.ocr import extract_headlines
from bot.post_to_x_api import post_with_api
from bot.post_via_ui import post_via_ui
from bot import db as DB

TIMEZONE = os.getenv("TIMEZONE", "America/New_York")
STORAGE_STATE = "auth.json"
OUT_DIR = "shots"

def has_api():
    needed = ["TWITTER_API_KEY","TWITTER_API_SECRET","TWITTER_ACCESS_TOKEN","TWITTER_ACCESS_SECRET"]
    return all(os.getenv(k) for k in needed)

def phash_for(image_path):
    return str(imagehash.phash(Image.open(image_path)))

def alt_text_for(headlines, ts_local):
    base = f"Screenshot of X 'Today's News' trending panel captured at {ts_local}."
    return base + (" Top items: " + "; ".join(headlines[:2]) if headlines else "")

def local_stamp(tz):
    now = datetime.datetime.now(pytz.timezone(tz))
    return now.strftime("%Y-%m-%d %I:%M %p %Z")

def run_once():
    DB.init_db()
    Path(OUT_DIR).mkdir(exist_ok=True)

    # 1) Capture
    img, ts_utc = capture_trending(STORAGE_STATE, OUT_DIR, timezone=TIMEZONE)
    phex = phash_for(img)

    # 2) De-dupe within 12h; recapture once if too similar
    if DB.find_similar(phex, threshold=3, within_hours=12) is not None:
        img, ts_utc = capture_trending(STORAGE_STATE, OUT_DIR, timezone=TIMEZONE)
        phex = phash_for(img)

    # 3) OCR headlines
    headlines = extract_headlines(img)

    # 4) Log capture
    cap_id = DB.log_capture(ts_utc, img, phex, headlines)

    # 5) A/B caption
    variant = choose_variant()
    caption = build_caption(variant, headlines, timezone=TIMEZONE)

    # 6) Post
    tweet_id = None
    if has_api():
        tweet_id = post_with_api(caption, img, alt_text_for(headlines, local_stamp(TIMEZONE)))
    else:
        # UI automation fallback (less reliable; prefer API)
        post_via_ui(STORAGE_STATE, caption, img)

    # 7) Persist post record with explicit UTC tzinfo
    posted_at_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    DB.log_post(cap_id, variant, caption, tweet_id, posted_at_iso)

if __name__ == "__main__":
    run_once()
