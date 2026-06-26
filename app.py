import streamlit as st
import pandas as pd
import re

# 1. 必须放在最前面：强制全宽，隐藏默认布局
st.set_page_config(page_title="电池数据自动化清洗分流中心", layout="wide", initial_sidebar_state="collapsed")

# 2. 🚨 核心修复：强制注入最高优先级的 CSS 全局样式，砸碎 Streamlit 的默认纯白皮肤
st.markdown("""
    <style>
    /* 彻底重写主体，强制变为图二的深邃暗夜弥散背景 */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 30%, #0f2042 60%, #1f1135 100%) !important;
        background-color: #0d1117 !important;
        color: #ffffff !important;
    }
    
    /* 隐藏 Streamlit 顶部多余的白条和页脚 */
    [data-testid="stHeader"], footer, [data-testid="stDecoration"] { 
        display: none !important; 
    }
    
    /* 重新规划全局内边距 */
    .block-container {
        padding: 2rem 5rem !important;
    }
    
    /* 强行复刻图二：高浓度、厚重白透磨砂玻璃大面板 */
    .premium-glass-card {
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(30px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(160%) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        padding: 30px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3) !important;
        margin-bottom: 25px !important;
    }
    
    /* 控制台和预览框内的文字全部锁死为高级黑/深灰 */
    .premium-glass-card *, .data-sub-card * {
        color: #000000 !important;
    }
    
    /* 顶层无衬线高级大标题 */
    .app-title {
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
        font-weight: 800 !important;
        font-size: 2.3rem !important;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -0.03em;
    }
    .app-subtitle {
        color: rgba(255, 255, 255, 0.4) !important;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 30px;
        letter-spacing: 0.15em;
    }
    
    /* 双表并排的高级半透明小卡片 */
    .data-sub-card {
        background: rgba(255, 255, 255, 0.96) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.7) !important;
    }
    .data-sub-card h3 {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        margin-bottom: 12px !important;
    }
    
    /* 强行美化 Streamlit 原生的灰色上传框 */
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(0, 0, 0, 0.03) !important;
        border: 2px dashed rgba(0, 0, 0, 0.15) !important;
        border-radius: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== 顶部文字标题（网页大底背景之上） ====================
st.markdown('<div class="app-title">电池数据自动化清洗分流中心</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">PREMIUM MINIMALIST DESIGN · SHIFTING AURORA</div>', unsafe_allow_html=True)

# ==================== 核心操控磨砂面板 ====================
st.markdown('<div class="premium-glass-card">', unsafe_allow_html=True)

col_file, col_opt1, col_opt2 = st.columns([1.5, 1, 1], gap="large")

with col_file:
    st.markdown("<b style='font-size:1rem;'>文件上传控制台</b>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("请选择或拖拽 Excel 表格 (.xlsx)", type=["xlsx"], label_visibility="collapsed")

with col_opt1:
    st.markdown("<b style='font-size:1rem;'>尺寸格式配置</b>", unsafe_allow_html=True)
    size_unit = st.selectbox("数据单位", ["保持 MM", "换算成 CM"], label_visibility="collapsed")
    size_prefix = st.checkbox("增加“长宽高”汉字前缀", value=True)

with col_opt2:
    st.markdown("<b style='font-size:1rem;'>续航解析配置</b>", unsafe_allow_html=True)
    range_mode = st.selectbox("数字解析模式", ["保留区间（如 80-100）", "只要最大值"], label_visibility="collapsed")
    range_unit = st.selectbox("后缀单位", ["大写 KM", "中文 公里", "纯数字"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== 下方结果分流展示区 ====================
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
            st.markdown(f'<p style="color:#ff4b4b; font-weight:700; text-align:center;">🛑 {brake_reason}</p>', unsafe_allow_html=True)
        else:
            res_df = pd.DataFrame(cleaned_data)
            lishi_df = res_df[res_df['款式'] == '立式'].drop(columns=['款式'])
            woshi_df = res_df[res_df['款式'] == '卧式'].drop(columns=['款式'])
            
            res_col1, res_col2 = st.columns(2, gap="large")
            with res_col1:
                st.markdown('<div class="data-sub-card"><h3>📊 立式电池分流中心</h3>', unsafe_allow_html=True)
                st.dataframe(lishi_df, use_container_width=True, height=260)
                csv_li = lishi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("导出立式数据 (.csv)", data=csv_li, file_name="立式_电池数据.csv", mime="text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with res_col2:
                st.markdown('<div class="data-sub-card"><h3>📊 卧式电池分流中心</h3>', unsafe_allow_html=True)
                st.dataframe(woshi_df, use_container_width=True, height=260)
                csv_wo = woshi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("导出卧式数据 (.csv)", data=csv_wo, file_name="卧式_电池数据.csv", mime="text/csv")
                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"表格读取故障: {e}")
else:
    st.markdown("""
        <div class="data-sub-card" style="text-align: center; padding: 40px 0; color: rgba(0,0,0,0.4); font-weight:600;">
            📥 请在上方控制台上传 Excel 表格文件，系统将自动清洗并在此展示双表分流结果
        </div>
    """, unsafe_allow_html=True)
