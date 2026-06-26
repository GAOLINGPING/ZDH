import streamlit as st
import pandas as pd
import re

# 强制全宽，锁死单屏
st.set_page_config(page_title="电池数据自动化清洗分流中心", layout="wide", initial_sidebar_state="collapsed")

# --- 🌟 完美复刻第二张图：高冷静谧微光 + 厚重极简纯净磨砂玻璃卡片 ---
st.markdown("""
    <style>
    /* 1. 静谧冷色调暗夜弥散渐变背景 */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0d1117, #161b22, #0f2042, #1f1135, #0b2e36) !important;
        background-size: 400% 400% !important;
        animation: slowGradient 20s ease infinite !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    @keyframes slowGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 隐藏所有多余组件 */
    [data-testid="stHeader"], footer, [data-testid="stDecoration"] { display: none !important; }
    
    .block-container {
        padding: 3rem 5rem 2rem 5rem !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
    }
    
    /* 2. 纯净厚重磨砂玻璃大卡片（高饱和白透，带精致微弱内描边） */
    .premium-apple-card {
        background: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(40px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
        border-radius: 28px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15) !important;
        padding: 2.5rem !important;
        margin: 0 auto !important;
        max-width: 1200px !important;
        width: 100%;
    }
    
    /* 3. 极简高级文字排版 */
    .main-title {
        color: #000000 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        letter-spacing: -0.04em;
        margin-bottom: 0.3rem;
        text-align: center;
    }
    .sub-title {
        color: rgba(0, 0, 0, 0.4) !important;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 2rem;
        text-align: center;
        letter-spacing: 0.05em;
    }

    /* 4. 下方数据展示精致独立卡片 */
    .result-section {
        display: flex;
        gap: 32px;
        max-width: 1200px;
        margin: 1.5rem auto 0 auto !important;
        width: 100%;
    }
    .data-sub-card {
        flex: 1;
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        padding: 1.5rem !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
    }
    .data-sub-card h3 {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #000000 !important;
        margin-bottom: 0.8rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== 页面头部 ====================
st.markdown('<h1 class="main-title">电池数据自动化清洗分流中心</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">PREMIUM MINIMALIST DESIGN · DATA AUTOMATION</p>', unsafe_allow_html=True)

# ==================== 中央操控大盘 ====================
st.markdown('<div class="premium-apple-card">', unsafe_allow_html=True)

col_file, col_opt1, col_opt2 = st.columns([1.6, 1, 1], gap="large")

with col_file:
    st.markdown("<span style='color:#000000; font-weight:700; font-size:1.05rem;'>文件上传</span>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("请拖拽或选择 Excel 文件 (.xlsx)", type=["xlsx"], label_visibility="collapsed")

with col_opt1:
    st.markdown("<span style='color:#000000; font-weight:700; font-size:1.05rem;'>尺寸格式配置</span>", unsafe_allow_html=True)
    size_unit = st.selectbox("单位处理", ["保持 MM", "换算成 CM"], label_visibility="collapsed")
    size_prefix = st.checkbox("加上“长宽高”汉字前缀", value=True)

with col_opt2:
    st.markdown("<span style='color:#000000; font-weight:700; font-size:1.05rem;'>续航数据模式</span>", unsafe_allow_html=True)
    range_mode = st.selectbox("数字解析", ["保留区间（如 80-100）", "只要最大值"], label_visibility="collapsed")
    range_unit = st.selectbox("单位选择", ["大写 KM", "中文 公里", "纯数字"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== 数据分流展示区 ====================
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        
        # 铁律：向下填充合并单元格
        df[0] = df[0].ffill()
        df[1] = df[1].ffill()
        df[2] = df[2].ffill()
        
        data_rows = df.iloc[3:].copy()
        cleaned_data = []
        brake_triggered = False
        brake_reason = ""

        for idx, row in data_rows.iterrows():
            style = str(row[2]).strip()
            if style not in ['立式', '卧式']: continue
                
            sku_text = str(row[9]).strip() if pd.notna(row[9]) else ""
            
            # --- 规格提取 ---
            v_raw = str(row[1]).strip().upper()
            v_str = v_raw if "V" in v_raw else (v_raw + "V" if v_raw.isdigit() else "未知V")
            if v_str == "未知V":
                v_m = re.search(r'(\d+)\s*V', sku_text, re.IGNORECASE)
                if v_m: v_str = v_m.group(1) + "V"

            ah_m = re.search(r'(\d+)\s*AH', sku_text, re.IGNORECASE)
            if not ah_m: ah_m = re.search(r'(\d+)\s*A(?!M)', sku_text, re.IGNORECASE)
            if not ah_m: ah_m = re.search(r'\d+\s*[vV]\s*(\d+)', sku_text)
            ah_str = ah_m.group(1) + "AH" if ah_m else "未知AH"
            spec = f"{v_str}{ah_str}"
            
            # --- 尺寸提取 ---
            size_raw = str(row[3]).strip()
            dims = re.split(r'[*xX×]', size_raw)
            if len(dims) != 3 or size_raw.isdigit():
                brake_triggered = True
                brake_reason = f"行 {idx+1} 尺寸异常: 【{size_raw}】，已触发安全刹车！"
                break
            try:
                d_nums = [float(d.strip()) for d in dims]
            except:
                brake_triggered = True
                brake_reason = f"行 {idx+1} 尺寸含非数字: 【{size_raw}】，已触发安全刹车！"
                break
                
            if size_unit == "换算成 CM":
                d_nums = [n / 10 for n in d_nums]
                d_strs = [str(int(n)) if n.is_integer() else str(n) for n in d_nums]
                unit_label = "CM"
            else:
                d_strs = [str(int(n)) if n.is_integer() else str(n) for n in d_nums]
                unit_label = "MM"
                
            if size_prefix:
                l_str, w_str, h_str = f"长{d_strs[0]}{unit_label}", f"宽{d_strs[1]}{unit_label}", f"高{d_strs[2]}{unit_label}"
            else:
                l_str, w_str, h_str = f"{d_strs[0]}{unit_label}", f"{d_strs[1]}{unit_label}", f"{d_strs[2]}{unit_label}"
                
            # --- 续航提取 ---
            range_m = re.search(r'([\d\-]+)\s*km', sku_text, re.IGNORECASE)
            if not range_m: range_m = re.search(r'([\d\-]+)\s*公里', sku_text)
            if range_m:
                raw_val = range_m.group(1)
                final_num = raw_val.split("-")[-1].strip() if range_mode == "只要最大值" and "-" in raw_val else raw_val
            else:
                final_num = "未知"
            u_suffix = "" if range_unit == "纯数字" else ("KM" if range_unit == "大写 KM" else "公里")
            range_final = f"{final_num}{u_suffix}" if final_num != "未知" else "未知"
            
            # --- 蓝牙提取 ---
            is_bluetooth = "TRUE" if "蓝牙" in sku_text or "蓝牙" in str(row[5]) else "FALSE"
            
            cleaned_data.append({
                "电池规格": spec, "款式": style, "长": l_str, "宽": w_str, "高": h_str, "续航": range_final, "蓝牙": is_bluetooth
            })
            
        if brake_triggered:
            st.markdown(f'<div style="max-width:1200px; margin:1rem auto;"><p style="color:#ff4b4b; font-weight:700;">🛑 {brake_reason}</p></div>', unsafe_allow_html=True)
        else:
            res_df = pd.DataFrame(cleaned_data)
            lishi_df = res_df[res_df['款式'] == '立式'].drop(columns=['款式'])
            woshi_df = res_df[res_df['款式'] == '卧式'].drop(columns=['款式'])
            
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.markdown('<div class="data-sub-card"><h3>立式电池数据</h3>', unsafe_allow_html=True)
                st.dataframe(lishi_df, use_container_width=True, height=220)
                csv_li = lishi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("下载立式数据 (.csv)", data=csv_li, file_name="立式_电池数据.csv", mime="text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with res_col2:
                st.markdown('<div class="data-sub-card"><h3>卧式电池数据</h3>', unsafe_allow_html=True)
                st.dataframe(woshi_df, use_container_width=True, height=220)
                csv_wo = woshi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("下载卧式数据 (.csv)", data=csv_wo, file_name="卧式_电池数据.csv", mime="text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"表格格式读取失败: {e}")
else:
    st.markdown("""
        <div class="result-section">
            <div class="data-sub-card" style="text-align: center; padding: 3rem 0; color: rgba(0,0,0,0.3); font-weight:600;">
                等待上传 Excel 表格文件以展示清洗分流结果...
            </div>
        </div>
    """, unsafe_allow_html=True)
