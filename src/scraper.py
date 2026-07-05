import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class B2BScraper:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]

    def scrape_yellowpages(self, keyword: str, location: str):
        formatted_keyword = keyword.replace(" ", "+")
        formatted_location = location.replace(" ", "+").replace(",", "%2C")
        url = f"https://www.yellowpages.com/search?search_terms={formatted_keyword}&geo_location_terms={formatted_location}"
        print(f"[LOG] 執行緒隔離爬蟲啟動: {url}")

        leads_data = []

        with sync_playwright() as p:
            # 💡 終極防禦：如果找不到專屬核心，直接強迫 Playwright 使用 Linux 系統自帶的 Chromium
            try:
                print("[LOG] 嘗試使用系統內建 Chromium 啟動...")
                browser = p.chromium.launch(
                    executable_path="/usr/bin/chromium", # Linux 系統標準的 chromium 安裝路徑
                    headless=True
                )
            except Exception as launch_err:
                print(f"[WARN] 指定路徑啟動失敗: {launch_err}，嘗試退回預設啟動...")
                # 備用方案：如果路徑不對，嘗試退回預設
                browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                user_agent=random.choice(self.user_agents),
                viewport={"width": 1280, "height": 800}
            )
            
            page = context.new_page()
            
            try:
                time.sleep(random.uniform(1.0, 2.5))
                response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
                print(f"[LOG] Playwright 狀態碼: {response.status}")
                
                if response.status != 200:
                    browser.close()
                    return []

                page.wait_for_timeout(1500)
                html_content = page.content()
                
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
                print(f"[CRITICAL] 執行緒內 Playwright 異常: {e}")
            finally:
                browser.close()

        return leads_data