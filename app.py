import streamlit as st
import plotly.express as px
import pandas as pd
import yfinance as yf

# 1. 設定網頁排版
st.set_page_config(page_title="最強投資決策系統", layout="wide")

st.title("🚀 最強投資決策輔助系統")
st.write("沒有穩賺不賠的明牌，但有最強的數據比較工具。一眼看穿誰才是真正的強勢標的！")
st.divider()

# --- 最強功能：多標的相對績效比較 ---
st.header("📊 標的績效大PK (基準化比較)")
st.write("請輸入你想比較的股票或 ETF 代號。系統會將它們放在同一個起跑點，讓你輕鬆看出誰的報酬率最有利。")

# 讓使用者輸入多個代號
tickers_input = st.text_input(
    "🔍 輸入多檔代號 (請用半形逗號隔開，例如：0050.TW, 2330.TW, 2317.TW 或 AAPL, MSFT, GOOG)", 
    "0050.TW, 2330.TW, 2317.TW"
)

if tickers_input:
    # 整理使用者輸入的代號清單
    ticker_list = [t.strip().upper() for t in tickers_input.split(",")]
    
    try:
        with st.spinner('正在從華爾街抓取數據並進行精密計算...'):
            # 一次下載多檔股票過去一年的「收盤價」
            data = yf.download(ticker_list, period="1y")['Close']
            
            # 檢查是否有抓不到資料的情況
            if data.empty:
                st.warning("⚠️ 抓不到資料，請確認代號格式是否正確（台股記得加 .TW）。")
            else:
                # 【核心邏輯】：將所有股票的第一天價格設為 100 (基準化)
                # 這樣無論股價是一千還是十塊，都能公平比較漲跌幅
                normalized_data = (data / data.iloc[0]) * 100
                
                # 重整資料以適應 Plotly 繪圖格式
                normalized_data = normalized_data.reset_index()
                # 將寬表格轉為長表格 (Tidy data)，方便畫多條線
                melted_data = normalized_data.melt(id_vars=['Date'], var_name='標的代號', value_name='相對報酬表現 (起點為100)')
                
                # 繪製相對績效折線圖
                fig = px.line(
                    melted_data, 
                    x='Date', 
                    y='相對報酬表現 (起點為100)', 
                    color='標的代號',
                    title="📈 近一年相對績效走勢 (數值 > 100 代表賺錢，< 100 代表虧損)"
                )
                
                # 優化圖表外觀
                fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="損益兩平線")
                st.plotly_chart(fig, use_container_width=True)
                
                # --- 附加功能：計算並顯示這段期間的總報酬率 ---
                st.subheader("🏆 最終報酬率排行榜")
                returns = ((data.iloc[-1] - data.iloc[0]) / data.iloc[0]) * 100
                returns_df = pd.DataFrame({'標的代號': returns.index, '近一年累積報酬率 (%)': returns.values})
                returns_df = returns_df.sort_values(by='近一年累積報酬率 (%)', ascending=False).reset_index(drop=True)
                
                # 格式化顯示為小數點後兩位
                st.dataframe(returns_df.style.format({'近一年累積報酬率 (%)': '{:.2f}%'}))

    except Exception as e:
        st.error("系統運算時發生錯誤，請確認輸入的代號是否都正確存在。")

st.divider()
st.caption("⚠️ **強力免責聲明**：本系統不保證獲利。歷史績效不代表未來報酬，投資決策請自行審慎評估風險。數據來源為 Yahoo Finance，可能存在延遲或誤差。")
