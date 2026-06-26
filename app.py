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
    size_unit = st.selectbox("单位转换", ["换算成 CM", "保持 MM"], label_visibility="collapsed")
    size_prefix = st.checkbox("加上“长宽高”文字前缀", value=True)

with col_opt2:
    st.markdown("<b style='color:#111;'>🔋 续航配置模式</b>", unsafe_allow_html=True)
    range_mode = st.selectbox("数字解析模式", ["保留区间（如 80-100）", "只要最大值"], label_visibility="collapsed")
    range_unit = st.selectbox("单位样式选择", ["大写 KM", "中文 公里", "纯数字"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)
st.write("") 

# ==================== 下方数据结果分流展示区 ====================
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
            
            # --- 尺寸提取与刹车 ---
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
            st.error(f"🛑 {brake_reason}")
        else:
            res_df = pd.DataFrame(cleaned_data)
            lishi_df = res_df[res_df['款式'] == '立式'].drop(columns=['款式'])
            woshi_df = res_df[res_df['款式'] == '卧式'].drop(columns=['款式'])
            
            # 渲染结果分流双卡片
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.markdown('<div class="sub-card"><h3>📋 立式分流数据</h3>', unsafe_allow_html=True)
                st.dataframe(lishi_df, use_container_width=True, height=200)
                csv_li = lishi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 下载立式表格 (.csv)", data=csv_li, file_name="立式_电池数据.csv", mime="text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with res_col2:
                st.markdown('<div class="sub-card"><h3>📋 卧式分流数据</h3>', unsafe_allow_html=True)
                st.dataframe(woshi_df, use_container_width=True, height=200)
                csv_wo = woshi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 下载卧式表格 (.csv)", data=csv_wo, file_name="卧式_电池数据.csv", mime="text/csv")
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"表格格式读取失败: {e}")
else:
    # 未上传状态时的占位提示，同样采用白透磨砂材质
    st.markdown("""
        <div class="result-container">
            <div class="sub-card" style="text-align: center; justify-content: center; color: rgba(0,0,0,0.4); font-size:1.05rem;">
                🔮 待上传文件... 上传成功后将在此无缝预览分流结果。
            </div>
        </div>
    """, unsafe_allow_html=True)
