import asyncio
import random
import time
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class B2BScraper:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]

    async def scrape_yellowpages(self, keyword: str, location: str):
        formatted_keyword = keyword.replace(" ", "+")
        formatted_location = location.replace(" ", "+").replace(",", "%2C")
        url = f"https://www.yellowpages.com/search?search_terms={formatted_keyword}&geo_location_terms={formatted_location}"
        print(f"[LOG] [Async] 正在啟動 Playwright 模擬瀏覽器: {url}")

        leads_data = []

        # 改用 async_playwright 建立完全隔離的異步環境
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=random.choice(self.user_agents),
                viewport={"width": 1280, "height": 800}
            )
            
            page = await context.new_page()
            
            try:
                # 異步等待
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                response = await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                print(f"[LOG] 攔截到狀態碼: {response.status}")
                
                if response.status != 200:
                    await browser.close()
                    return []

                await page.wait_for_timeout(1500)
                html_content = await page.content()
                
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
                print(f"[CRITICAL] Async Playwright 異常: {e}")
            finally:
                await browser.close()

        return leads_data