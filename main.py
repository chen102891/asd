import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import time
import json

products = [
    {"id": "SSZS-52268", "name": "YOASOBI SSZS-52268（衣服）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52268?ima=0302", "has_size": True},
    {"id": "SSZS-52265", "name": "YOASOBI SSZS-52265（衣服）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52265?ima=0326", "has_size": True},
    {"id": "SSZS-52282", "name": "YOASOBI SSZS-52282（無尺寸）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52282?ima=0215", "has_size": False},
    {"id": "SSZS-52280", "name": "YOASOBI SSZS-52280（無尺寸）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52280?ima=0506", "has_size": False},
]

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")
INTERVAL = 60  # 每 60 秒檢查一次
STATUS_FILE = "last_status.json"

def check_product(product):
    try:
        resp = requests.get(product["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        if product["has_size"]:
            sizes = [label.get_text(strip=True) for label in soup.select("label.size_btn") if "在庫なし" not in label.get_text()]
            return bool(sizes)
        else:
            btn = soup.select_one("button.btn-curve.cart")
            return btn and "在庫なし" not in btn.get_text()
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
        print("✅ Email 已發送")
    except Exception as e:
        print("⚠️ Email 發送失敗：", e)

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {p["id"]: False for p in products}

def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def main():
    print("🛒 YOASOBI 補貨監控中（Render 版本）")
    last_status = load_status()
    is_first_run = True

    while True:
        messages = []
        new_status = {}

        for p in products:
            in_stock = check_product(p)
            new_status[p["id"]] = in_stock

            if in_stock and not last_status.get(p["id"], False):
                if not is_first_run:
                    messages.append(f"{p['name']} 有貨啦！\n🔗 {p['url']}")

        if messages:
            send_email("【YOASOBI 補貨通知】以下商品有貨啦！", "\n\n".join(messages))
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 尚無補貨")

        save_status(new_status)
        last_status = new_status
        is_first_run = False
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
