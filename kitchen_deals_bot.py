# kitchen_deals_bot.py
import os, time, sqlite3, hashlib, re, requests, feedparser

# ==== CONFIGURE THESE ====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")           # from @BotFather
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")       # e.g. @MyKitchenDeals
AMAZON_TAG = os.getenv("AMAZON_TAG")                   # e.g. mytag-20

# Kitchen & cooking related RSS feeds
RSS_FEEDS = [
    "https://slickdeals.net/newsearch.php?src=SearchBarV2&q=kitchen&pp=30&sort=newest&rss=1",
    "https://www.reddit.com/r/Cooking/.rss",
    "https://www.reddit.com/r/CookingDeals/.rss",
    "https://www.reddit.com/r/BBQ/.rss",
    "https://www.reddit.com/r/grilling/.rss"
]

DB_PATH = "seen.sqlite3"

def ensure_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY, ts INTEGER)")
    con.commit(); con.close()

def seen_before(uid: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.execute("SELECT 1 FROM seen WHERE id=?", (uid,))
    row = cur.fetchone()
    con.close()
    return row is not None

def mark_seen(uid: str):
    con = sqlite3.connect(DB_PATH)
    con.execute("INSERT OR IGNORE INTO seen(id, ts) VALUES (?,?)", (uid, int(time.time())))
    con.commit(); con.close()

def normalize_affiliate(url: str) -> str:
    if "amazon." in url:
        if "tag=" not in url and AMAZON_TAG:
            joiner = "&" if "?" in url else "?"
            url = f"{url}{joiner}tag={AMAZON_TAG}"
    return url

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def post_to_telegram(text: str):
    token = TELEGRAM_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    if not token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID environment variables.")
    api = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(api, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": False})
    r.raise_for_status()

def entry_uid(e) -> str:
    base = (e.get("title","") + "|" + e.get("link",""))
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def pick_entries():
    all_entries = []
    for feed in RSS_FEEDS:
        try:
            d = feedparser.parse(feed)
            for e in d.entries[:20]:
                all_entries.append(e)
        except Exception:
            continue
    def etime(e):
        p = getattr(e, "published_parsed", None)
        return time.mktime(p) if p else 0
    return sorted(all_entries, key=etime, reverse=True)

def main_once():
    ensure_db()
    posted = 0
    for e in pick_entries():
        uid = entry_uid(e)
        if seen_before(uid):
            continue
        title = clean_text(e.get("title",""))
        link = e.get("link","")
        if not link or not title:
            mark_seen(uid); continue
        link = normalize_affiliate(link)
        if len(title) < 10: 
            mark_seen(uid); continue
        text = f"🍳 {title}
{link}"
        try:
            post_to_telegram(text)
            mark_seen(uid)
            posted += 1
            time.sleep(2)
            if posted >= 3:
                break
        except Exception:
            continue

if __name__ == "__main__":
    main_once()
