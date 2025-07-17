import requests
from bs4 import BeautifulSoup

# 僅保留一筆商品作測試（has_size=True）
product = {
    "name": "YOASOBI SSZS-52268（衣服）",
    "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52268?ima=0302",
    "id": "SSZS-52268",
    "has_size": True
}

def check_product(p):
    try:
        resp = requests.get(p["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        if p["has_size"]:
            labels = soup.select("label.size_btn")
            print(f"共找到 {len(labels)} 個尺寸選項")
            for i, label in enumerate(labels):
                print(f"  [{i}] -> {label.get_text(strip=True)}")

            l_label = next((label for label in labels if "L" in label.get_text()), None)
            if l_label:
                l_text = l_label.get_text(strip=True)
                print(f"👉 找到 L 標籤：{l_text}")
                if any(term in l_text for term in ["在庫なし", "販売しておりません"]):
                    print("❌ L 尺寸沒貨")
                    return False
                else:
                    print("✅ L 尺寸有貨！")
                    return True
            else:
                print("⚠️ 沒有找到 L 尺寸")
                return False
        else:
            print("⚠️ 商品不含尺寸，請檢查設定")
            return False
    except Exception as e:
        print(f"⚠️ 檢查失敗：{p['url']}\n{e}")
        return False

# 執行測試
check_product(product)
