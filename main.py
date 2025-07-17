import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import time
import json

products = [
    {"name": "YOASOBI SSZS-52268（衣服）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52268?ima=0302", "id": "SSZS-52268", "has_size": True},
    {"name": "YOASOBI SSZS-52265（衣服）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52265?ima=0326", "id": "SSZS-52265", "has_size": True},
    {"name": "YOASOBI SSZS-52282（無尺寸）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52282?ima=0215", "id": "SSZS-52282", "has_size": False},
    {"name": "YOASOBI SSZS-52280（無尺寸）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52280?ima=0506", "id": "SSZS-52280", "has_size": False},
    {"name": "YOASOBI SSZS-52277（無尺寸）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52277?ima=0122", "id": "SSZS-52277", "has_size": False},
]

STATUS_FILE = "last_status.json"
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")
INTERVAL = 30  # 每 30秒檢查一次

# 讀取上次的庫存狀態
def load_last_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {p["id"]: False for p in products}

# 儲存最新的庫存狀態
def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f)

# 檢查單一商品
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

# 寄信
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

def main():
    print("🛒 YOASOBI 補貨監控中（Render 版本）")
    last_status = load_last_status()

    while True:
        new_status = {}
        messages = []

        for p in products:
            in_stock = check_product(p)
            new_status[p["id"]] = in_stock
            if in_stock and not last_status.get(p["id"], False):
                msg = f"🛍️ {p['name']} 有貨！\n🔗 {p['url']}"
                messages.append(msg)

        if messages:
            send_email("【YOASOBI 補貨通知】以下商品有貨啦！", "\n\n".join(messages))
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 尚無補貨")

        save_status(new_status)
        last_status = new_status
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
