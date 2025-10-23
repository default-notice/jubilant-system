import sqlite3, os, json, datetime, pathlib

STATE_DIR = pathlib.Path(".bot_state"); STATE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = os.getenv("BOT_DB_PATH", str(STATE_DIR / "bot.sqlite3"))

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS captures(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  image_path TEXT NOT NULL,
  phash TEXT NOT NULL,
  headlines TEXT
);
CREATE TABLE IF NOT EXISTS posts(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  capture_id INTEGER NOT NULL,
  variant TEXT NOT NULL,
  caption TEXT NOT NULL,
  tweet_id TEXT,
  posted_at TEXT NOT NULL,
  FOREIGN KEY(capture_id) REFERENCES captures(id)
);
CREATE TABLE IF NOT EXISTS metrics(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  like_count INTEGER, reply_count INTEGER, retweet_count INTEGER, quote_count INTEGER,
  fetched_at TEXT NOT NULL,
  FOREIGN KEY(post_id) REFERENCES posts(id)
);
"""

def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with _conn() as c:
        c.executescript(SCHEMA)

def log_capture(ts_iso, image_path, phash, headlines):
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO captures(ts,image_path,phash,headlines) VALUES (?,?,?,?)",
            (ts_iso, image_path, phash, json.dumps(headlines)))
        return cur.lastrowid

def find_similar(phash, threshold=3, within_hours=12):
    from imagehash import hex_to_hash
    now = datetime.datetime.utcnow()
    since = (now - datetime.timedelta(hours=within_hours)).isoformat()
    with _conn() as c:
        rows = c.execute("SELECT id, phash FROM captures WHERE ts >= ? ORDER BY id DESC", (since,)).fetchall()
    target = hex_to_hash(phash)
    for r in rows:
        try:
            if target - hex_to_hash(r["phash"]) <= threshold:
                return r["id"]
        except Exception:
            continue
    return None

def log_post(capture_id, variant, caption, tweet_id, posted_at_iso):
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO posts(capture_id,variant,caption,tweet_id,posted_at) VALUES (?,?,?,?,?)",
            (capture_id, variant, caption, tweet_id, posted_at_iso))
        return cur.lastrowid

def latest_posts_without_metrics(limit=120):
    with _conn() as c:
        rows = c.execute("""
          SELECT p.id, p.tweet_id, p.posted_at
          FROM posts p
          LEFT JOIN metrics m ON m.post_id = p.id
          WHERE p.tweet_id IS NOT NULL AND m.id IS NULL
          ORDER BY p.posted_at DESC
          LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

def store_metrics(post_id, like_count, reply_count, retweet_count, quote_count):
    ts = datetime.datetime.utcnow().isoformat()
    with _conn() as c:
        c.execute(
            "INSERT INTO metrics(post_id,like_count,reply_count,retweet_count,quote_count,fetched_at) VALUES (?,?,?,?,?,?)",
            (post_id, like_count, reply_count, retweet_count, quote_count, ts))

def posts_last_days(days=7):
    since = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat()
    with _conn() as c:
        rows = c.execute("""
          SELECT p.id, p.variant, p.tweet_id, p.caption, p.posted_at,
                 IFNULL(m.like_count,0) AS like_count, IFNULL(m.reply_count,0) AS reply_count,
                 IFNULL(m.retweet_count,0) AS retweet_count, IFNULL(m.quote_count,0) AS quote_count
          FROM posts p
          LEFT JOIN metrics m ON m.post_id = p.id
          WHERE p.posted_at >= ?
        """, (since,)).fetchall()
        return [dict(r) for r in rows]
