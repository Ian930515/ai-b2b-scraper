import time
import random
import requests
from bs4 import BeautifulSoup

class B2BScraper:
    def __init__(self):
        # 偽裝成真實瀏覽器的請求標頭池
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]

    def scrape_yellowpages(self, keyword: str, location: str):
        formatted_keyword = keyword.replace(" ", "+")
        formatted_location = location.replace(" ", "+").replace(",", "%2C")
        url = f"https://www.yellowpages.com/search?search_terms={formatted_keyword}&geo_location_terms={formatted_location}"
        print(f"[LOG] 輕量化強健爬蟲啟動: {url}")

        leads_data = []
        
        # 設定請求標頭，完美模擬真人瀏覽行為
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        try:
            # 隨機延時防反爬
            time.sleep(random.uniform(1.0, 2.0))
            
            # 發送請求 (設定 timeout 避免死鎖)
            response = requests.get(url, headers=headers, timeout=15)
            print(f"[LOG] 伺服器回應狀態碼: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[ERROR] 請求失敗，狀態碼: {response.status_code}")
                return []

            # 解析網頁原始碼
            soup = BeautifulSoup(response.text, "html.parser")
            search_results = soup.find_all("div", class_="result")
            print(f"[LOG] 成功定位到原始 DOM 節點共 {len(search_results)} 個")
            
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
                except Exception as inner_err:
                    print(f"[WARN] 單筆資料解析異常: {inner_err}")
                    continue

        except Exception as e:
            print(f"[CRITICAL] 爬蟲核心執行發生異常: {e}")

        return leads_data

if __name__ == "__main__":
    scraper = B2BScraper()
    results = scraper.scrape_yellowpages("Digital Marketing", "New York, NY")
    print(f"測試結果共: {len(results)} 筆")