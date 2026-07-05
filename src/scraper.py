import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import os

class B2BScraper:
    def __init__(self):
        # 保留 User-Agent 池，讓 Playwright 啟動時隨機帶入
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]

def scrape_yellowpages(self, keyword: str, location: str):
        formatted_keyword = keyword.replace(" ", "+")
        formatted_location = location.replace(" ", "+").replace(",", "%2C")
        url = f"https://www.yellowpages.com/search?search_terms={formatted_keyword}&geo_location_terms={formatted_location}"
        print(f"[LOG] 正在啟動 Playwright 模擬瀏覽器: {url}")

        # ⭕ 正確位置：放在 with 之外！每次執行前先強迫系統補齊依賴與 Chromium
        print("[LOG] 正在雲端環境初始化 Playwright 系統依賴 (含系統庫)...")
        os.system("playwright install chromium --with-deps")

        leads_data = []

        # 進入純粹的自動化控制流程
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=random.choice(self.user_agents),
                viewport={"width": 1280, "height": 800}
            )
            
            page = context.new_page()
            
            try:
                # 關鍵細節：加上隨機等待，並引導瀏覽器前往目標網頁
                time.sleep(random.uniform(1.0, 2.5))
                
                # wait_until="domcontentloaded" 代表網頁 HTML 載入完就開始解析，不用等廣告或圖片載入，速度更快
                response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
                
                print(f"[LOG] Playwright 攔截到伺服器狀態碼: {response.status}")
                
                if response.status != 200:
                    print(f"[ERROR] 模擬瀏覽器請求失敗，狀態碼: {response.status}")
                    browser.close()
                    return []

                # 讓網頁稍微停頓，確保內部的 JS 執行完畢
                page.wait_for_timeout(1500)
                
                # 取得網頁目前的完整 HTML 原始碼
                html_content = page.content()
                
                # 接下來無縫接軌我們原本的 BeautifulSoup 解析邏輯！
                soup = BeautifulSoup(html_content, "html.parser")
                search_results = soup.find_all("div", class_="result")
                
                for result in search_results:
                    try:
                        name_tag = result.find("a", class_="business-name")
                        name = name_tag.get_text(strip=True) if name_tag else "N/A"
                        
                        phone_tag = result.find("div", class_="phones")
                        phone = phone_tag.get_text(strip=True) if phone_tag else "N/A"
                        
                        links_div = result.find("div", class_="links")
                        website_tag = links_div.find("a", class_="track-visit-website") if links_div else None
                        website = website_tag["href"] if website_tag else "N/A"

                        if name != "N/A":
                            leads_data.append({
                                "company_name": name,
                                "phone": phone,
                                "website": website
                            })
                    except Exception:
                        continue

            except Exception as e:
                print(f"[CRITICAL] Playwright 執行發生異常: {e}")
            
            finally:
                # 良好的資工素養：一定要記得關閉瀏覽器，否則記憶體會洩漏（Memory Leak）
                browser.close()

        return leads_data

if __name__ == "__main__":
    # 本地直接測試
    scraper = B2BScraper()
    results = scraper.scrape_yellowpages("Digital Marketing", "New York")
    print(f"測試抓取結果共: {len(results)} 筆")