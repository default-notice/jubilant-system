from datetime import datetime, timedelta, timezone
from bot.post_to_x_api import fetch_public_metrics
from bot import db as DB

AGE_HOURS_MIN = 20  # wait so numbers aren't near-zero

def main():
    DB.init_db()
    pending = DB.latest_posts_without_metrics(limit=120)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=AGE_HOURS_MIN)
    for p in pending:
        try:
            posted = datetime.fromisoformat(p["posted_at"])
        except Exception:
            continue
        if posted > cutoff:
            continue  # too fresh; pick it up tomorrow
        if not p["tweet_id"]:
            continue
        try:
            pm = fetch_public_metrics(p["tweet_id"])
            DB.store_metrics(
                post_id=p["id"],
                like_count=pm.get("like_count",0),
                reply_count=pm.get("reply_count",0),
                retweet_count=pm.get("retweet_count", pm.get("repost_count",0)),
                quote_count=pm.get("quote_count",0),
            )
        except Exception as e:
            print("Metrics failed for", p["tweet_id"], e)

if __name__ == "__main__":
    main()
