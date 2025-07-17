import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import time
import json

# 測試用單一商品
products = [
    {"name": "YOASOBI SSZS-52268（衣服）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52268?ima=0302", "id": "SSZS-52268", "has_size": True},
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

# 檢查單一商品庫存
def check_product(product):
    try:
        resp = requests.get(product["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        if product["has_size"]:
            alerts = soup.select("div.alert_box p.alert")
            for alert in alerts:
                l_text = alert.get_text(strip=True)
                print(f"🔍 尺寸狀態：{l_text}")
                if "L" in l_text:
                    if "在庫なし" in l_text:
                        print("❌ L 尺寸沒貨")
                        return False
                    else:
                        print("✅ L 尺寸有貨")
                        return True
            print("❓ 找不到 L 尺寸標籤")
            return False
        else:
            btn = soup.select_one("button.btn-curve.cart")
            return btn and "在庫なし" not in btn.get_text()

    except Exception as e:
        print(f"⚠️ 檢查失敗：{product['url']}\n{e}")
        return False

# 寄送 Email
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
    print("🛒 YOASOBI 補貨監控中（L 尺寸專用）")
    last_status = load_last_status()

    while True:
        new_status = {}
        messages = []

        for p in products:
            in_stock = check_product(p)
            new_status[p["id"]] = in_stock
            if in_stock and not last_status.get(p["id"], False):
                msg = f"🛍️ {p['name']} L 尺寸有貨！\n🔗 {p['url']}"
                messages.append(msg)

        if messages:
            send_email("【YOASOBI 補貨通知】L 尺寸有貨啦！", "\n\n".join(messages))
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 尚無補貨")

        save_status(new_status)
        last_status = new_status
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
