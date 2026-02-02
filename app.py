import streamlit as st
import pandas as pd
from orchestrator import StockAnalysisOrchestrator
from utils.visualizer import create_unified_chart
import datetime

st.set_page_config(page_title="綜合股票分析系統", layout="wide")

st.title("🚀 綜合股票分析系統")
st.markdown("---")

# 初始化 Orchestrator
@st.cache_resource
def get_orchestrator():
    return StockAnalysisOrchestrator()

orchestrator = get_orchestrator()

# 側邊欄：搜尋股票
st.sidebar.header("搜尋股票")
stock_id = st.sidebar.text_input("請輸入股票代號 (例如: 2330)", value="2330")

if st.sidebar.button("開始分析"):
    with st.spinner(f"正在分析股票 {stock_id}，請稍候..."):
        result = orchestrator.run_full_analysis(stock_id)
        
        if "error" in result:
            st.error(result["error"])
        else:
            # 取得基礎數據用於畫圖
            price_data = orchestrator.data_manager.get_stock_data(stock_id)
            
            # 顯示主要資訊
            col1, col2, col3 = st.columns(3)
            col1.metric("目前價格", f"{result['current_price']:.2f}")
            col2.metric("預測趨勢", result['prediction']['final_trend'])
            col3.metric("分析進度", "100%")

            st.markdown("---")

            # 1. 綜合圖表
            st.subheader("📊 統一分析看板")
            
            # 讓用戶選擇要顯示在圖表上的分析師
            analyst_names = [a['analyst'] for a in result['analysis']]
            selected_analysts = st.sidebar.multiselect(
                "選擇圖表標記分析師",
                options=analyst_names,
                default=analyst_names
            )
            
            fig = create_unified_chart(price_data, result['analysis'], visible_analysts=selected_analysts)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # 2. 分析師詳細說明
            st.subheader("👨‍🏫 分析師專業觀點")
            
            # 使用 Tabs 顯示不同分析師
            tabs = st.tabs(analyst_names)
            
            for i, tab in enumerate(tabs):
                a_result = result['analysis'][i]
                with tab:
                    # 根據預測決定顏色
                    pred_color = "red" if a_result['prediction'] == "看多" else ("green" if a_result['prediction'] == "看空" else "white")
                    st.markdown(f"### {a_result['analyst']} 的建議：:{pred_color}[**{a_result['prediction']}**]")
                    st.write(f"**綜合評分：** {a_result['score']}")
                    st.info(a_result['explanation'])
                    
                    # 顯示具體指標
                    st.write("**核心指標：**")
                    cols = st.columns(len(a_result['indicators']))
                    for idx, (k, v) in enumerate(a_result['indicators'].items()):
                        with cols[idx]:
                            st.metric(k, f"{v:.2f}" if isinstance(v, float) else v)

            st.markdown("---")

            # 3. 三大法人與新聞
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("🏢 三大法人動向")
                if result['institutional']:
                    inst_df = pd.DataFrame(result['institutional'])
                    st.dataframe(inst_df.tail(10))
                else:
                    st.write("無三大法人數據。")
            
            with col_b:
                st.subheader("📰 新聞情緒摘要")
                st.write(result['news_summary'])
                st.write("詳細新聞請參閱 FinMind 平台。")

else:
    st.info("請在左側輸入股票代號並點擊「開始分析」。")

st.sidebar.markdown("---")
st.sidebar.write("數據來源：FinMind API (台股), yfinance (備援)")
