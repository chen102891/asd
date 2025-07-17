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
    {"name": "YOASOBI SSZS-52277（毛巾）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52277?ima=0122", "id": "SSZS-52277", "has_size": False},
]

STATUS_FILE = "last_status.json"
INTERVAL = 60  # 每 1 分鐘檢查一次

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
        resp = requests.get(product["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        if product["has_size"]:
            alerts = soup.select("div.alert_box p.alert")
            found = False
            for alert in alerts:
                text = alert.get_text(strip=True)
                print(f"🔍 尺寸狀態：{text}")
                if any(size in text for size in ["M", "L"]) and "在庫なし" not in text:
                    print(f"✅ 尺寸有貨！➡ {text}")
                    found = True
            if not found:
                print("❌ M / L 都沒貨")
            return found
        else:
            btn = soup.select_one("button.btn-curve.cart")
            return btn and "在庫なし" not in btn.get_text()

    except Exception as e:
        print(f"⚠️ 檢查失敗：{product['url']}\n{e}")
        return False

# 暫時停用寄信功能
def send_email(subject, body):
    print("📧（暫不寄信）通知內容如下：")
    print(subject)
    print(body)

def main():
    print("🛒 YOASOBI 補貨監控中（M / L 尺寸 + 無尺寸商品）")
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
            # send_email("【YOASOBI 補貨通知】以下商品有貨啦！", "\n\n".join(messages))
            print("✅ 補貨通知（模擬）:")
            print("\n\n".join(messages))
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 尚無補貨")

        save_status(new_status)
        last_status = new_status
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

