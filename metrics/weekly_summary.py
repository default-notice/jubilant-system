import datetime
from pathlib import Path
from bot import db as DB

def summarize(days=7):
    rows = DB.posts_last_days(days)
    for r in rows:
        r["total"] = (r["like_count"] + r["reply_count"] + r["retweet_count"] + r["quote_count"])
    byv = {"A":[],"B":[]}
    for r in rows:
        byv.setdefault(r["variant"],[]).append(r)
    def agg(rs): 
        return {"n":len(rs), "avg": (sum(x["total"] for x in rs)/len(rs)) if rs else 0}
    a, b = agg(byv.get("A",[])), agg(byv.get("B",[]))
    top = sorted(rows, key=lambda r:r["total"], reverse=True)[:5]
    lines = [f"# Weekly Trending Bot Report ({datetime.date.today().isoformat()})",
             "", "Window: last 7 days", "",
             "## A/B performance",
             f"- Variant A: {a['n']} posts, avg interactions: {a['avg']:.2f}",
             f"- Variant B: {b['n']} posts, avg interactions: {b['avg']:.2f}",
             "", "## Top 5 posts"]
    for r in top:
        url = f" | https://x.com/i/web/status/{r['tweet_id']}" if r.get("tweet_id") else ""
        lines.append(f"- {r['posted_at']} | Variant {r['variant']} | total={r['total']} (likes {r['like_count']}, replies {r['reply_count']}, rts {r['retweet_count']}, quotes {r['quote_count']}){url}")
    return "\n".join(lines)

def main():
    DB.init_db()
    Path("reports").mkdir(parents=True, exist_ok=True)
    out = Path("reports")/f"weekly_report_{datetime.date.today().isoformat()}.md"
    out.write_text(summarize(7), encoding="utf-8")
    print("Wrote", out)

if __name__ == "__main__":
    main()
