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
    {"name": "YOASOBI SSZS-52277（毛巾）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52277?ima=0122", "id": "SSZS-52277", "has_size": False},
]

STATUS_FILE = "last_status.json"
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")
INTERVAL = 60  # 每 1 分鐘檢查一次

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
    print(f"\n🔎 檢查商品： {product['name']}")
    try:
        resp = requests.get(product["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        if product["has_size"]:
            found_sizes = []
            available = []
            for p_tag in soup.select("div.alert_box p.alert"):
                text = p_tag.get_text(strip=True)
                match = re.match(r"([SML])\s*\((.+)\)", text)
                if match:
                    size = match.group(1)
                    status = match.group(2)
                    print(f"🔍 尺寸狀態：{size}（{status}）")
                    found_sizes.append(size)
                    if size in ["M", "L"] and "在庫なし" not in status:
                        available.append(size)

            if available:
                for size in available:
                    print(f"✅ {size} 尺寸有貨！")
                return True
            else:
                print("❌ M / L 都沒貨")
                return False

        else:
            alert_box = soup.select_one("div.alert_box p.alert")
            if alert_box and "在庫なし" in alert_box.get_text():
                print("❌ 無尺寸商品沒貨（頁面寫明在庫なし）")
                return False
            else:
                print("✅ 無尺寸商品有貨！")
                return True

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
                msg = f"\n🛍️ {p['name']} 有貨！\n🔗 {p['url']}"
                messages.append(msg)
            elif not in_stock:
                unstocked.append(f"🔸 {p['name']} 尚無補貨")

        if messages:
            print("\n✅ 補貨通知（模擬）:")
            print("\n".join(messages))
        else:
            print(f"\n[{time.strftime('%H:%M:%S')}] 尚無補貨")

        if unstocked:
            print("\n📭 尚未補貨商品：")
            for u in unstocked:
                print(u)

        save_status(new_status)
        last_status = new_status
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

