import os
import requests
from bs4 import BeautifulSoup
import time
from collections import deque

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.dubizzle.com.eg/en/mobile-phones-tablets-accessories-numbers/mobile-phones/cairo/q-iphone/"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

seen_ads = deque(maxlen=500)

def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=5
        )
    except Exception as e:
        print("Telegram Error:", e)

def normalize(link):
    if link.startswith("/en"):
        link = link.replace("/en", "")
    return "https://www.dubizzle.com.eg" + link

while True:
    try:
        res = session.get(URL, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")

        for ad in soup.select("li"):
            a = ad.select_one('a[href*="/ad/"]')
            if not a:
                continue

            link = normalize(a["href"])

            if link in seen_ads:
                continue

            seen_ads.append(link)

            title = "No title"
            if a.has_attr("title"):
                title = a["title"]

            img = ad.find("img")
            if title == "No title" and img and img.has_attr("alt"):
                title = img["alt"]

            price = "No price"
            for s in ad.find_all("span"):
                t = s.get_text(strip=True)
                if "EGP" in t or "ج.م" in t:
                    price = t
                    break

            send(f"📍 القاهرة\n📱 {title}\n💰 {price}\n🔗 {link}")
            print("Sent:", title)

        time.sleep(3)

    except Exception as e:
        print("Error:", e)
        time.sleep(3)
