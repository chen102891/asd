import requests
from bs4 import BeautifulSoup
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
            status_list = soup.select("div.alert_box p.alert")
            found_m = found_l = False

            for tag in status_list:
                text = tag.get_text(strip=True)
                print(f"🔍 尺寸狀態：{text}")
                if "M" in text and "在庫なし" not in text:
                    found_m = True
                if "L" in text and "在庫なし" not in text:
                    found_l = True

            if found_m or found_l:
                if found_m and found_l:
                    print("✅ M / L 尺寸有貨！")
                elif found_m:
                    print("✅ M 尺寸有貨！")
                elif found_l:
                    print("✅ L 尺寸有貨！")
                return True
            else:
                print("❌ M / L 都沒貨")
                return False
        else:
            btn = soup.select_one("button.btn-curve.cart")
            if btn and "在庫なし" not in btn.get_text():
                print("✅ 無尺寸商品有貨！")
                return True
            else:
                print("❌ 無尺寸商品沒貨")
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

        for p in products:
            print("\n🔎 檢查商品：", p["name"])
            in_stock = check_product(p)
            new_status[p["id"]] = in_stock
            if in_stock and not last_status.get(p["id"], False):
                msg = f"🛍️ {p['name']} 有貨！\n🔗 {p['url']}"
                messages.append(msg)

        if messages:
            print("\n✅ 補貨通知（模擬）:\n")
            print("\n\n".join(messages))
        else:
            print(f"\n[{time.strftime('%H:%M:%S')}] 尚無補貨")

        # 顯示未補貨商品
        unavailable = [p["name"] for p in products if not new_status.get(p["id"], False)]
        if unavailable:
            print("\n❌ 尚未補貨的商品：")
            for name in unavailable:
                print(f"- {name}")

        save_status(new_status)
        last_status = new_status
        time.sleep(INTERVAL)

if __name__ == "__main__":
    import os
    main()
