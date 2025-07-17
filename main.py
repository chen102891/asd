import requests
from bs4 import BeautifulSoup

# 僅保留一筆商品作測試（has_size=True）
product = {
    "name": "YOASOBI SSZS-52268（衣服）",
    "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52268?ima=0302",
    "id": "SSZS-52268",
    "has_size": True
}

def check_product(product):
    try:
        resp = requests.get(product["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        if product["has_size"]:
            labels = soup.select("label.size_btn")
            print(f"共找到 {len(labels)} 個尺寸選項")

            for idx, label in enumerate(labels):
                l_text = label.get_text(strip=True)
                print(f"[{idx}] -> {l_text}")

                if "L" in l_text:
                    print(f"👉 找到 L 標籤: {l_text}")
                    if "在庫なし" not in l_text:
                        print("✅ L 尺寸有貨！")
                        return True
                    else:
                        print("❌ L 尺寸無貨")
                        return False
            print("⚠️ 未找到 L 尺寸")
            return False
        else:
            btn = soup.select_one("button.btn-curve.cart")
            return btn and "在庫なし" not in btn.get_text()

    except Exception as e:
        print(f"⚠️ 檢查失敗：{product['url']}\n{e}")
        return False
        
# 執行測試
check_product(product)
