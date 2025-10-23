from bot.post_to_x_api import fetch_public_metrics
from bot import db as DB
from datetime import datetime, timedelta, timezone
import os

REFRESH_COUNT = int(os.getenv("METRICS_REFRESH_PER_WEEK", "6"))  # keep Free cap safe even in 5-week months
WINDOW_DAYS = int(os.getenv("METRICS_REFRESH_WINDOW_DAYS", "14"))

def main():
    DB.init_db()
    rows = DB.posts_last_days(WINDOW_DAYS)
    for r in rows:
        r["total"] = (r.get("like_count",0)+r.get("reply_count",0)
                      +r.get("retweet_count",0)+r.get("quote_count",0))
    now = datetime.now(timezone.utc)
    eligible = []
    for r in rows:
        try:
            posted = datetime.fromisoformat(r["posted_at"])
        except Exception:
            continue
        if (now - posted).total_seconds() < 24*3600:
            continue
        if not r.get("tweet_id"):
            continue
        eligible.append(r)
    eligible.sort(key=lambda x: (x["total"], x["posted_at"]), reverse=True)
    for r in eligible[:REFRESH_COUNT]:
        try:
            pm = fetch_public_metrics(r["tweet_id"])
            DB.store_metrics(
                post_id=r["id"],
                like_count=pm.get("like_count",0),
                reply_count=pm.get("reply_count",0),
                retweet_count=pm.get("retweet_count", pm.get("repost_count",0)),
                quote_count=pm.get("quote_count",0),
            )
        except Exception as e:
            print("Refresh failed for", r["tweet_id"], e)

if __name__ == "__main__":
    main()
