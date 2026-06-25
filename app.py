import streamlit as st
import pandas as pd
import re

# 强制全宽，锁死单屏
st.set_page_config(page_title="电池数据自动化清洗分流中心", layout="wide", initial_sidebar_state="collapsed")

# --- 🌟 霓虹弥散背景 + 极简纯净磨砂玻璃 CSS 魔改 ---
st.markdown("""
    <style>
    /* 1. 动态霓虹弥散渐变背景 */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(125deg, #ff7b90, #ae77ff, #60c3ff, #00ea9a) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 15s ease infinite !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 隐藏页眉和页脚 */
    [data-testid="stHeader"], footer, [data-testid="stDecoration"] { display: none !important; }
    
    .block-container {
        padding: 2.5rem 4rem 1.5rem 4rem !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
    }
    
    /* 2. 扁平极简白色磨砂玻璃大卡片（无描边，更纯净） */
    .apple-card {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(30px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(160%) !important;
        border-radius: 24px !important;
        border: none !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04) !important;
        padding: 2rem !important;
        margin: 0 auto !important;
        max-width: 1200px !important;
        width: 100%;
    }
    
    /* 3. 标题样式 */
    .main-title {
        color: #111111 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        letter-spacing: -0.03em;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: rgba(0, 0, 0, 0.5);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* 4. 下方分流结果卡片样式 */
    .result-container {
        display: flex;
        gap: 24px;
        max-width: 1200px;
        margin: 0 auto !important;
        width: 100%;
        height: 42vh !important;
        margin-bottom: 1rem !important;
    }
    .sub-card {
        flex: 1;
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 1.2rem !important;
        display: flex;
        flex-direction: column;
        height: 100%;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.03) !important;
    }
    .sub-card h3 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #111111 !important;
        margin-bottom: 0.6rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== 页面头部 ====================
st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">电池数据自动化清洗分流中心</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Neon Gradient Style · 严格遵循配置铁律校验</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 中央操控卡片（扁平玻璃风格） ====================
st.markdown('<div class="apple-card">', unsafe_allow_html=True)

col_file, col_opt1, col_opt2 = st.columns([1.8, 1, 1], gap="large")

with col_file:
    uploaded_file = st.file_uploader("📥 将 Excel 表格拖拽至此处上传 (.xlsx)", type=["xlsx"])

with col_opt1:
    st.markdown("<b style='color:#111;'>📐 尺寸配置方案</b>", unsafe_allow_html=True)
    size_unit = st.selectbox("单位转换",
