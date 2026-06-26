import streamlit as st
import pandas as pd
import re
import base64

# 1. 锁死全宽，干掉系统默认多余白边
st.set_page_config(page_title="电池数据清洗中心", layout="wide", initial_sidebar_state="collapsed")

# 2. 彻底接管网页样式：强制注入图二的高冷深邃暗夜底色
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(140deg, #0b0f19 0%, #111827 40%, #071630 80%, #160d29 100%) !important;
        background-color: #0b0f19 !important;
        color: #ffffff !important;
    }
    [data-testid="stHeader"], footer, [data-testid="stDecoration"] { display: none !important; }
    .block-container { padding: 2.5rem 5rem !important; }
    
    /* 强行抹去系统文件上传器多余的灰色背景，只留纯粹功能 */
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 2px dashed rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: rgba(255,255,255,0.7) !important; }
    
    /* 彻底重构：图二中高纯度、厚重白透的磨砂卡片大外壳 */
    .premium-glass-card {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(40px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
        border-radius: 24px !important;
        padding: 35px !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 30px !important;
        width: 100%;
    }
    
    /* 大操盘内的标签文字：全部锁死为高级加粗黑 */
    .control-label {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        margin-bottom: 8px;
        display: block;
    }
    
    /* 顶层高冷排版标题 */
    .app-title {
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
        font-weight: 800 !important;
        font-size: 2.4rem !important;
        text-align: center;
        letter-spacing: -0.03em;
        margin-bottom: 5px;
    }
    .app-subtitle {
        color: rgba(255, 255, 255, 0.35) !important;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 35px;
        letter-spacing: 0.15em;
    }
    
    /* 🚨 核心秘密：用自定义 HTML 彻底重写表格，击碎官方巨丑的灰色原生表格 */
    .custom-table-container {
        background: rgba(255, 255, 255, 0.98) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15) !important;
        width: 100%;
        margin-top: 10px;
    }
    .custom-table-title {
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        color: #000000 !important;
        margin-bottom: 15px !important;
    }
    .apple-style-table {
        width: 100%;
        border-collapse: collapse !important;
        margin-bottom: 20px;
    }
    .apple-style-table th {
        background-color: #f5f5f7 !important;
        color: #1d1d1f !important;
        font-weight: 700 !important;
        text-align: left !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        border: none !important;
    }
    .apple-style-table td {
        padding: 14px 16px !important;
        color: #000000 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        border-bottom: 1px solid #e8e8ed !important;
    }
    .apple-style-table tr:last-child td {
        border-bottom: none !important;
    }
    
    /* 自定义纯平大按钮 */
    .custom-download-btn {
        display: inline-block;
        background: #000000 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
        border-radius: 10px !important;
        text-decoration: none !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease;
        text-align: center;
    }
    .custom-download-btn:hover {
        background: #232325 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== 顶层标题排版 ====================
st.markdown('<div class="app-title">电池数据自动化清洗分流中心</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">PREMIUM MINIMALIST HARDWARE CONTROL PANEL</div>', unsafe_allow_html=True)

# ==================== 图二同款：中央大操盘 ====================
st.markdown('<div class="premium-glass-card">', unsafe_allow_html=True)

col_file, col_opt1, col_opt2 = st.columns([1.6, 1, 1], gap="large")

with col_file:
    st.markdown('<span class="control-label">文件上传控制台</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("请选择或拖拽 Excel 表格 (.xlsx)", type=["xlsx"], label_visibility="collapsed")

with col_opt1:
    st.markdown('<span class="control-label">尺寸单位配置</span>', unsafe_allow_html=True)
    size_unit = st.selectbox("单位转换", ["保持 MM", "换算成 CM"], label_visibility="collapsed")
    size_prefix = st.checkbox("增加“长宽高”汉字前缀", value=True)

with col_opt2:
    st.markdown('<span class="control-label">续航数据解析</span>', unsafe_allow_html=True)
    range_mode = st.selectbox("数字过滤", ["保留区间（如 80-100）", "只要最大值"], label_visibility="collapsed")
    range_unit = st.selectbox("后缀单位", ["大写 KM", "中文 公里", "纯数字"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== 函数：将生成的 DataFrame 强行渲染成纯净的 HTML 高级表格 ====================
def render_custom_table(dataframe, title, filename):
    csv_data = dataframe.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv_data.encode('utf-8-sig')).decode()
    download_href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="custom-download-btn">📥 导出清洗后表格 (.csv)</a>'
    
    # 构建纯净、100%可控的 HTML 表格
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
    html_str += f'<div style="text-align: right; margin-top: 15px;">{download_href}</div>'
    html_str += '</div>'
    return html_str

# ==================== 自动化核心逻辑区 ====================
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        
        # 填充单元格合并
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
            st.markdown(f'<p style="color:#ff4b4b; font-weight:700; text-align:center; font-size:1.1rem; margin-top:20px;">🛑 {brake_reason}</p>', unsafe_allow_html=True)
        else:
            res_df = pd.DataFrame(cleaned_data)
            lishi_df = res_df[res_df['款式'] == '立式'].drop(columns=['款式'])
            woshi_df = res_df[res_df['款式'] == '卧式'].drop(columns=['款式'])
            
            # 双列布局，完美吐出 HTML 精致双表格
            res_col1, res_col2 = st.columns(2, gap="large")
            with res_col1:
                st.markdown(render_custom_table(lishi_df, "📊 立式电池自动清洗中心", "立式_电池数据.csv"), unsafe_allow_html=True)
            with res_col2:
                st.markdown(render_custom_table(woshi_df, "📊 卧式电池自动清洗中心", "卧式_电池数据.csv"), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"表格格式读取失败，请检查结构: {e}")
else:
    # 默认状态卡片
    st.markdown("""
        <div class="custom-table-container" style="text-align: center; padding: 50px 0; color: rgba(0,0,0,0.4); font-weight:700; font-size:1.05rem;">
            📥 请在上方白色大盘中上传 Excel 电池原始数据，系统将自动彻底清洗并在此生成图二同款纯净双表
        </div>
    """, unsafe_allow_html=True)
