import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import time
import json
import re

products = [
    {"name": "YOASOBI SSZS-52268（衣服）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52268?ima=0302", "id": "SSZS-52268", "has_size": True},
    {"name": "YOASOBI SSZS-52265（衣服）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52265?ima=0326", "id": "SSZS-52265", "has_size": True},
    {"name": "YOASOBI SSZS-52282（無尺寸）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52282?ima=0215", "id": "SSZS-52282", "has_size": False},
    {"name": "YOASOBI SSZS-52280（無尺寸）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52280?ima=0506", "id": "SSZS-52280", "has_size": False},
]

STATUS_FILE = "last_status.json"
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")
INTERVAL = 60


def load_last_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {p["id"]: False for p in products}


def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f)


def check_product(product):
    try:
        print(f"\n🔎 檢查商品： {product['name']}")
        resp = requests.get(product["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        if product["has_size"]:
            size_alerts = soup.select("div.alert_box p.alert")
            size_found = {"M": False, "L": False}
            for p in size_alerts:
                text = p.get_text(strip=True)
                print(f"🔍 尺寸狀態：{text}")
                m = re.match(r"([SML])\s*\((.+)\)", text)
                if m:
                    size = m.group(1)
                    status = m.group(2)
                    if size in size_found and "在庫なし" not in status:
                        size_found[size] = True

            if size_found["M"]:
                print("✅ M 尺寸有貨！")
            if size_found["L"]:
                print("✅ L 尺寸有貨！")
            if not size_found["M"] and not size_found["L"]:
                print("❌ M / L 都沒貨")

            return size_found["M"] or size_found["L"]

        else:
            alert_texts = [p.get_text(strip=True) for p in soup.select("div.alert_box p.alert")]
            if any("在庫なし" in t for t in alert_texts):
                print("❌ 無尺寸商品沒貨（頁面寫明在庫なし）")
                return False
            print("✅ 無尺寸商品有貨！")
            return True

    except Exception as e:
        print(f"⚠️ 檢查失敗：{product['url']}\n{e}")
        return False


def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 Email 已發送")
    except Exception as e:
        print("⚠️ Email 發送失敗：", e)


def main():
    print("\n🛒 YOASOBI 補貨監控中（M / L 尺寸 + 無尺寸商品）")
    last_status = load_last_status()

    while True:
        new_status = {}
        messages = []
        unstocked = []

        for p in products:
            in_stock = check_product(p)
            new_status[p["id"]] = in_stock
            if in_stock and not last_status.get(p["id"], False):
                messages.append(f"🛍️ {p['name']} 有貨！\n🔗 {p['url']}")
            if not in_stock:
                unstocked.append(p["name"])

        if messages:
            print("\n✅ 補貨通知：\n")
            for m in messages:
                print(m + "\n")
            send_email("【YOASOBI 補貨通知】以下商品有貨啦！", "\n\n".join(messages))
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 尚無補貨")

        if unstocked:
            print("\n📭 尚未補貨商品：")
            for name in unstocked:
                print(f"🔸 {name} 尚無補貨")

        save_status(new_status)
        last_status = new_status
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
