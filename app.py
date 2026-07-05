import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from src.scraper import B2BScraper
from src.ai_analyzer import LeadAnalyzer

# 1. 網頁基本設定
st.set_page_config(
    page_title="AI B2B Leads Intelligence Scraper",
    page_icon="🔍",
    layout="wide"
)

# 2. 標題與介紹區塊
st.title("🔍 AI-Powered B2B Leads Intelligence Scraper")
st.markdown("""
這個系統能幫助歐美 B2B 業主快速挖掘潛在客戶。透過 **Python 爬蟲** 自動抓取公開黃頁數據，
並結合 **OpenAI 核心大模型** 進行商業痛點分析，自動化生成精準的開發名單！
""")

st.divider()

# 3. 側邊欄輸入區
st.sidebar.header("🎯 搜尋參數設定")
keyword = st.sidebar.text_input("搜尋產業關鍵字 (e.g., Cafe, Dental, Marketing)", "Digital Marketing")
location = st.sidebar.text_input("搜尋地理位置 (e.g., New York, NY)", "New York, NY")

start_button = st.sidebar.button("🚀 開始挖掘與 AI 分析")

# 4. 主要顯示邏輯
if start_button:
    scraper = B2BScraper()
    analyzer = LeadAnalyzer()
    
    # 💡 隔離執行緒：避開 Streamlit Cloud 內建 Event Loop 的衝突
    with st.spinner("🕵️‍♂️ 正在隔離執行緒中安全爬取網頁數據中，請稍候..."):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(scraper.scrape_yellowpages, keyword, location)
            raw_leads = future.result()
        
    if not raw_leads:
        st.error("❌ 抱歉，未能抓取到任何資料，請檢查關鍵字或網路連線。")
    else:
        st.success(f"✅ 成功抓取到 {len(raw_leads)} 筆原始名單！")
        
        # 步驟二：跑 AI 分析
        with st.spinner("🤖 正在啟動 AI 智能大腦，進行商業痛點評估與打分..."):
            final_reports = analyzer.analyze_leads(raw_leads)
            
        # 步驟三：資料轉換與視覺化
        df = pd.DataFrame(final_reports)
        cols = ['company_name', 'lead_score', 'primary_pain_point', 'action_suggestion', 'phone', 'website']
        df = df[cols]
        
        # 顯示指標小卡
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="總挖掘名單數", value=f"{len(df)} 筆")
        with col2:
            high_value_count = len(df[df['lead_score'] >= 4])
            st.metric(label="🔥 高價值潛在客戶 (4分以上)", value=f"{high_value_count} 筆")
            
        # 顯示互動式數據表格
        st.subheader("📊 智能 B2B 客戶情報面板")
        st.dataframe(
            df,
            column_config={
                "company_name": "公司名稱",
                "lead_score": st.column_config.NumberColumn("潛在價值評分 (1-5)", format="%d ⭐"),
                "primary_pain_point": "AI 診斷核心痛點",
                "action_suggestion": "建議開發策略",
                "phone": "聯絡電話",
                "website": st.column_config.LinkColumn("官方網站")
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.divider()
        st.subheader("💾 匯出名單資料")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        
        st.download_button(
            label="📥 下載精準客戶情報 Excel (CSV)",
            data=csv,
            file_name=f"B2B_Leads_{keyword.replace(' ', '_')}.csv",
            mime="text/csv"
        )
else:
    st.info("💡 請在左側輸入你想挖掘的行業與地區，並點擊「開始挖掘與 AI 分析」按鈕。")
