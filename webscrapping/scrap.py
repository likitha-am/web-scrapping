import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta, timezone
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------- EMAIL SETTINGS ----------------
SENDER_EMAIL = "amlikitha520@gmail.com"
RECEIVER_EMAIL = "amlikitha520@gmail.com"
APP_PASSWORD = "ktpk bpub wthd rild"  # Google App Password

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    title TEXT,
                    url TEXT,
                    summary TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    # Ensure summary column exists
    c.execute("PRAGMA table_info(articles)")
    columns = [col[1] for col in c.fetchall()]
    if "summary" not in columns:
        c.execute("ALTER TABLE articles ADD COLUMN summary TEXT")
    conn.commit()
    conn.close()

# ---------------- INSERT INTO DB ----------------
def insert_article(source, title, url, summary=""):
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    c.execute("SELECT id FROM articles WHERE url = ?", (url,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO articles (source, title, url, summary) VALUES (?, ?, ?, ?)",
            (source, title, url, summary)
        )
        conn.commit()
    conn.close()

# ---------------- SCRAPERS ----------------
def scrape_firstpost():
    url = "https://www.firstpost.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, timeout=15, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for h2 in soup.select("h2 a"):
            title = h2.get_text(strip=True)
            link = h2["href"]
            if link.startswith("/"):
                link = "https://www.firstpost.com" + link

            # Grab multi-paragraph summary
            try:
                article_resp = requests.get(link, timeout=10, headers=headers)
                article_soup = BeautifulSoup(article_resp.text, "html.parser")
                paragraphs = article_soup.find_all("p")
                summary = " ".join(p.get_text(strip=True) for p in paragraphs[:5])
            except Exception as e:
                print(f"Error fetching article {link}: {e}")
                summary = ""

            insert_article("Firstpost", title, link, summary)

    except Exception as e:
        print("Error scraping Firstpost:", e)


def scrape_brut():
    url = "https://www.brut.media/en"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, timeout=15, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for card in soup.select(".card, .media-card"):
            try:
                a = card.find("a", href=True)
                if not a:
                    continue
                title = a.get_text(strip=True)
                link = a["href"]
                if link.startswith("/"):
                    link = "https://www.brut.media" + link
                # Brut summary optional (short titles usually)
                insert_article("Brut", title, link, "")
            except Exception as e:
                print("Error processing Brut card:", e)

    except Exception as e:
        print("Error scraping Brut:", e)

# ---------------- EMAIL SENDER ----------------
def send_email(subject, articles):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    # Build HTML body with styling
    if not articles:
        html = "<p>No new articles today. ✅</p>"
    else:
        html = """
        <div style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.5; color: #333;">
        <h2 style="color: #2E86C1;">📰 Your Daily News Digest</h2>
        """
        for art in articles:
            html += f"""
            <div style="margin-bottom: 25px;">
                <p>
                    <strong style="font-size: 18px;">[{art['source']}]</strong>
                    <a href="{art['url']}" style="font-size: 18px; color: #2874A6; text-decoration: none;">{art['title']}</a>
                </p>
                <p style="font-size: 15px; color: #555;">{art.get('summary','')}</p>
                <hr style="border: 0; border-top: 1px solid #ccc;">
            </div>
            """
        html += "</div>"

    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Email failed:", e)

# ---------------- DAILY DIGEST ----------------
def send_daily_news():
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute("SELECT source, title, url, summary FROM articles WHERE timestamp > ?", (yesterday,))
    rows = c.fetchall()
    conn.close()

    articles = [{"source": src, "title": title, "url": url, "summary": summary} for src, title, url, summary in rows]
    send_email("📰 Your Daily News Digest", articles)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    init_db()
    print("Scraping started...")
    scrape_firstpost()
    time.sleep(2)
    scrape_brut()
    print("Scraping finished! Data stored in news.db")
    send_daily_news()
