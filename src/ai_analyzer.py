import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

class LeadAnalyzer:
    def __init__(self):
        # 從環境變數讀取 Key，如果讀不到就拋出錯誤提醒
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-proj-xxx"):
            print("[WARNING] 未檢測到有效的 OPENAI_API_KEY，將啟用 Mock 模式進行測試。")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

    def analyze_leads(self, raw_leads: list) -> list:
        """
        將爬蟲抓到的原始名單丟給 AI，進行商業價值評估與結構化分類
        """
        if not self.client:
            # 如果沒有 API Key，我們寫一個 Mock 模擬回傳，確保同學在本地沒有 Key 也能把流程跑完！
            return self._get_mock_analysis(raw_leads)

        # 建立一個高階工程師必備的嚴謹 Prompt
        system_instruction = (
            "You are an expert B2B Growth Hacking Consultant. Your job is to analyze potential leads.\n"
            "Identify if they need web development, SEO, or advertising services based on their data.\n"
            "You MUST respond ONLY in a valid JSON array of objects. Do not include markdown blocks like ```json."
        )

        user_content = f"Analyze these raw leads and add fields 'lead_score' (1-5), 'primary_pain_point', and 'action_suggestion':\n{json.dumps(raw_leads, ensure_ascii=False)}"

        try:
            # 呼叫最新一代的 GPT 模型 (這裡用平價且快速的 gpt-4o-mini)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2 # 低隨機性，確保輸出的 JSON 格式穩定
            )

            # 解析 AI 回傳的字串並轉成 Python List
            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)

        except Exception as e:
            print(f"[ERROR] AI 分析發生異常: {e}")
            return self._get_mock_analysis(raw_leads)

    def _get_mock_analysis(self, raw_leads: list) -> list:
        """ 模擬 AI 分析的在地測試方法（防止沒有 Key 時程式卡死） """
        analyzed_results = []
        for lead in raw_leads:
            score = 5 if lead['website'] == 'N/A' else 2
            pain = "缺少官方網站，無法進行線上引流" if lead['website'] == 'N/A' else "官方網站為第三方託管，SEO 權重低"
            suggest = "主動致電推銷 RWD 響應式網頁設計方案" if lead['website'] == 'N/A' else "推銷獨立網域架站與品牌優化方案"
            
            analyzed_results.append({
                **lead,
                "lead_score": score,
                "primary_pain_point": pain,
                "action_suggestion": suggest
            })
        return analyzed_results

# 本地測試
if __name__ == "__main__":
    # 模擬你剛剛抓到的真實資料
    test_data = [
        {'company_name': 'OvationMR', 'phone': 'N/A', 'website': 'N/A'},
        {'company_name': 'Street1940 Digital Marketing Agency', 'phone': '(332) 333-5894', 'website': '[http://street1940digitalmarketingagency.localsearch.com](http://street1940digitalmarketingagency.localsearch.com)'},
        {'company_name': '5Boro Digital Marketing', 'phone': '(914) 200-3610', 'website': '[https://5borodigital.com](https://5borodigital.com)'}
    ]
    
    analyzer = LeadAnalyzer()
    print("\n[LOG] 開始進行 AI 數據分析...")
    final_reports = analyzer.analyze_leads(test_data)
    
    print("\n[SUCCESS] AI 分析完成，最終結果：")
    print(json.dumps(final_reports, indent=4, ensure_ascii=False))