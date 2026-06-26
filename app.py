import streamlit as st
import pandas as pd
import re
import base64

# 1. 锁死最高布局级别，隐藏多余默认组件
st.set_page_config(page_title="电池数据清洗中心", layout="wide", initial_sidebar_state="collapsed")

# 2. 🚨 终极暴力破解：穿透 Shadow 样式墙，强行剥离 Streamlit 所有原生的灰色、描边和刺眼白块
st.markdown("""
    <style>
    /* 强行平铺图二同款：静谧冷色调深邃暗夜弥散渐变底色 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(140deg, #070a12 0%, #0f141c 35%, #051226 75%, #120921 100%) !important;
        background-color: #070a12 !important;
        color: #ffffff !important;
    }
    [data-testid="stHeader"], footer, [data-testid="stDecoration"] { display: none !important; }
    .block-container { padding: 3rem 6rem !important; }
    
    /* 彻底清洗系统文件上传区的恶心灰色和边框，使其融入磨砂大盘 */
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(0, 0, 0, 0.04) !important;
        border: 2px dashed rgba(0, 0, 0, 0.12) !important;
        border-radius: 16px !important;
        box-shadow: none !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: rgba(0, 0, 0, 0.6) !important; font-weight: 500 !important; }
    
    /* 🌟 核心：强行拔除 Streamlit 灰色下拉框、复选框的原始丑陋样式 */
    div[data-baseweb="select"] > div {
        background-color: rgba(0, 0, 0, 0.04) !important;
        border: none !important;
        border-radius: 12px !important;
        color: #000000 !important;
        box-shadow: none !important;
    }
    div[data-baseweb="select"] * { color: #000000 !important; font-weight: 600 !important; }
    div[data-testid="stCheckbox"] label span {
        border-color: rgba(0, 0, 0, 0.2) !important;
    }
    
    /* 💎 终极复刻图二：高纯度、厚重平铺的白透磨砂玻璃控制大面板 */
    .premium-glass-card {
        background: rgba(255, 255, 255, 0.96) !important;
        backdrop-filter: blur(50px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(50px) saturate(200%) !important;
        border-radius: 28px !important;
        padding: 40px !important;
        box-shadow: 0 30px 70px rgba(0, 0, 0, 0.45) !important;
        margin-bottom: 35px !important;
        width: 100%;
        border: none !important; /* 彻底消灭任何外描边 */
    }
    
    .control-label {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        margin-bottom: 12px;
        display: block;
        letter-spacing: -0.02em;
    }
    
    /* 顶层无衬线高端排版 */
    .app-title {
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif;
        font-weight: 900 !important;
        font-size: 2.6rem !important;
        text-align: center;
        letter-spacing: -0.04em;
        margin-bottom: 6px;
    }
    .app-subtitle {
        color: rgba(255, 255, 255, 0.3) !important;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 40px;
        letter-spacing: 0.2em;
        font-weight: 600;
    }
    
    /* 🚨 彻底击碎系统原生表格：用 100% 纯净可控的 HTML 构建平铺无描边表格 */
    .custom-table-container {
        background: rgba(255, 255, 255, 0.98) !important;
        border-radius: 24px !important;
        padding: 28px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2) !important;
        width: 100%;
        margin-top: 10px;
        border: none !important;
    }
    .custom-table-title {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #000000 !important;
        margin-bottom: 18px !important;
        letter-spacing: -0.02em;
    }
    .apple-style-table {
        width: 100%;
        border-collapse: collapse !important;
        margin-bottom: 25px;
    }
    .apple-style-table th {
        background-color: #f4f4f7 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        text-align: left !important;
        padding: 14px 18px !important;
        font-size: 0.95rem !important;
        border: none !important;
    }
    .apple-style-table td {
        padding: 16px 18px !important;
        color: #1c1c1e !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        border-bottom: 1px solid #e5e5ea !important;
    }
    .apple-style-table tr:last-child td {
        border-bottom: none !important;
    }
    
    /* 极简无描边纯黑扁平按钮 */
    .custom-download-btn {
        display: inline-block;
        background: #000000 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 12px 26px !important;
        border-radius: 12px !important;
        text-decoration: none !important;
        font-size: 0.9rem !important;
        transition: background 0.2s ease;
        text-align: center;
    }
    .custom-download-btn:hover {
        background: #2c2c2e !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== 顶层大厂视觉排版 ====================
st.markdown('<div class="app-title">电池数据自动化清洗分流中心</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">AUTOMATED DATA ENGINE · MINIMAL DESIGN</div>', unsafe_allow_html=True)

# ==================== 彻底美化后的中央操控盘 ====================
st.markdown('<div class="premium-glass-card">', unsafe_allow_html=True)

col_file, col_opt1, col_opt2 = st.columns([1.6, 1, 1], gap="large")

with col_file:
    st.markdown('<span class="control-label">原始文件导入</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("请选择或拖拽 Excel 表格 (.xlsx)", type=["xlsx"], label_visibility="collapsed")

with col_opt1:
    st.markdown('<span class="control-label">尺寸格式转换</span>', unsafe_allow_html=True)
    size_unit = st.selectbox("单位规范", ["保持 MM", "换算成 CM"], label_visibility="collapsed")
    size_prefix = st.checkbox("注入“长宽高”汉字前缀", value=True)

with col_opt2:
    st.markdown('<span class="control-label">续航里程解析</span>', unsafe_allow_html=True)
    range_mode = st.selectbox("数字解析模式", ["保留区间（如 80-100）", "只要最大值"], label_visibility="collapsed")
    range_unit = st.selectbox("显示后缀", ["大写 KM", "中文 公里", "纯数字"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== HTML 自定义高级表格渲染逻辑 ====================
def render_custom_table(dataframe, title, filename):
    csv_data = dataframe.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv_data.encode('utf-8-sig')).decode()
    download_href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="custom-download-btn">📥 导出规范化表格 (.csv)</a>'
    
    html_str = f'<div class="custom-table-container">'
    html_str += f'<div class="custom-table-title">{title}</div>'
    html_str += '<table class="apple-style-table"><thead><tr>'
    for col in dataframe.columns:
        html_str += f'<th>{col}</th>'
    html_str += '</tr></thead><tbody>'
    
    for _, row in dataframe.iterrows():
        html_str += '<tr>'
        for cell in row:
            html_str += f'<td>{cell}</td>'
        html_str += '</tr>'
    html_str += '</tbody></table>'
    html_str += f'<div style="text-align: right; margin-top: 10px;">{download_href}</div>'
    html_str += '</div>'
    return html_str

# ==================== 自动化核心后端引擎 ====================
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        
        # 铁律填充
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
                brake_reason = f"第 {idx+1} 行尺寸字段异常: 【{size_raw}】，系统已紧急安全刹车！"
                break
            try:
                d_nums = [float(d.strip()) for d in dims]
            except:
                brake_triggered = True
                brake_reason = f"第 {idx+1} 行尺寸包含非法字符: 【{size_raw}】，系统已紧急安全刹车！"
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
            st.markdown(f'<p style="color:#ff4b4b; font-weight:800; text-align:center; font-size:1.15rem; margin-top:25px;">🛑 {brake_reason}</p>', unsafe_allow_html=True)
        else:
            res_df = pd.DataFrame(cleaned_data)
            lishi_df = res_df[res_df['款式'] == '立式'].drop(columns=['款式'])
            woshi_df = res_df[res_df['款式'] == '卧式'].drop(columns=['款式'])
            
            # 完美的双列 HTML 平铺高级大盘展示
            res_col1, res_col2 = st.columns(2, gap="large")
            with res_col1:
                st.markdown(render_custom_table(lishi_df, "📊 立式电池自动清洗分流结果", "立式_电池数据.csv"), unsafe_allow_html=True)
            with res_col2:
                st.markdown(render_custom_table(woshi_df, "📊 卧式电池自动清洗分流结果", "卧式_电池数据.csv"), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"解析发生未知错误: {e}")
else:
    st.markdown("""
        <div class="custom-table-container" style="text-align: center; padding: 60px 0; color: rgba(0,0,0,0.4); font-weight:800; font-size:1.1rem;">
            📥 请在上方控制大盘中拖入原始 Excel 表格，系统将自动彻底清洗，并在此生成图二同款纯净分流面板
        </div>
    """, unsafe_allow_html=True)
