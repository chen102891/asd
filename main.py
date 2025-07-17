import requests
from bs4 import BeautifulSoup
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
    print(f"\n🔎 檢查商品： {product['name']}")
    try:
        resp = requests.get(product["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        if product["has_size"]:
            labels = soup.select("label.size_btn")
            size_statuses = []
            for label in labels:
                text = label.get_text(strip=True)
                size_statuses.append(text)
                print(f"🔍 尺寸狀態：{text}")

            has_m = any("M" in t and "在庫なし" not in t for t in size_statuses)
            has_l = any("L" in t and "在庫なし" not in t for t in size_statuses)

            if has_m or has_l:
                if has_m: print("✅ M 尺寸有貨！")
                if has_l: print("✅ L 尺寸有貨！")
                return True
            else:
                print("❌ M / L 都沒貨")
                return False

        else:
            alert_box = soup.select_one("div.alert_box")
            if alert_box and "在庫なし" in alert_box.get_text():
                print("❌ 無尺寸商品沒貨（頁面寫明在庫なし）")
                return False

            btn = soup.select_one("button.btn-curve.cart")
            if btn and "在庫なし" not in btn.get_text():
                print("✅ 無尺寸商品有貨！")
                return True
            else:
                print("❌ 無尺寸商品沒貨（按鈕判斷）")
                return False

    except Exception as e:
        print(f"⚠️ 檢查失敗：{product['url']}\n{e}")
        return False

def main():
    print("🛒 YOASOBI 補貨監控中（M / L 尺寸 + 無尺寸商品）")
    last_status = load_last_status()

    while True:
        new_status = {}
        messages = []
        not_found = []

        for p in products:
            in_stock = check_product(p)
            new_status[p["id"]] = in_stock

            if in_stock and not last_status.get(p["id"], False):
                msg = f"\n🛍️ {p['name']} 有貨！\n🔗 {p['url']}\n"
                messages.append(msg)
            if not in_stock:
                not_found.append(f"🔸 {p['name']} 尚無補貨")

        # 模擬寄信：只印出訊息
        if messages:
            print("\n✅ 補貨通知（模擬）:")
            for m in messages:
                print(m)

        if not_found:
            print("\n📭 尚未補貨商品：")
            for item in not_found:
                print(item)

        print(f"\n[{time.strftime('%H:%M:%S')}] 尚無補貨")
        save_status(new_status)
        last_status = new_status
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
