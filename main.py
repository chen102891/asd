import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import time

products = [
    {"name": "YOASOBI SSZS-52268（衣服）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52268?ima=0302", "has_size": True},
    {"name": "YOASOBI SSZS-52265（衣服）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52265?ima=0326", "has_size": True},
    {"name": "YOASOBI SSZS-52282（無尺寸）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52282?ima=0215", "has_size": False},
    {"name": "YOASOBI SSZS-52280（無尺寸）", "url": "https://yoasobi-onlinestore.com/s/n135ec/item/detail/SSZS-52280?ima=0506", "has_size": False},
]

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")
INTERVAL = 60  # 每1分鐘檢查一次

def check_product(product):
    try:
        resp = requests.get(product["url"], headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        if product["has_size"]:
            sizes = [label.get_text(strip=True) for label in soup.select("label.size_btn") if "在庫なし" not in label.get_text()]
            if sizes:
                return f"🎽 {product['name']} 有貨！尺寸：{', '.join(sizes)}\n🔗 {product['url']}"
        else:
            btn = soup.select_one("button.btn-curve.cart")
            if btn and "在庫なし" not in btn.get_text():
                return f"🎁 {product['name']} 有貨（無尺寸）\n🔗 {product['url']}"
    except Exception as e:
        print(f"⚠️ 檢查失敗：{product['url']}\n{e}")
    return None

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
    while True:
        messages = [check_product(p) for p in products if check_product(p)]
        if messages:
            send_email("【YOASOBI 補貨通知】以下商品有貨啦！", "\n\n".join(messages))
        else:
            print(f"[{time.strftime('%H:%M:%S')}] 尚無補貨")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
