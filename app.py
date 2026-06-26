import streamlit as st
import pandas as pd
import re
import io

# 强制全宽，注入苹果磨砂玻璃及单屏无滚动样式
st.set_page_config(page_title="电池数据清洗中心", layout="wide", initial_sidebar_state="collapsed")

# --- 🌟 核心样式魔改：注入顶级 Apple 视觉和锁死单屏机制 ---
st.markdown("""
    <style>
    /* 1. 彻底干掉 Streamlit 默认的各种边距、页眉和滚动条 */
    [data-testid="stAppViewContainer"] {
        background: linear_gradient(135deg, #e0e5ec 0%, #f0f4f8 100%) !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    [data-testid="stHeader"], footer {display: none !important;}
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important; /* 均匀分布，绝不超出 */
    }
    
    /* 2. 顶栏标题设计 */
    .title-container {
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .title-container h1 {
        color: #1d1d1f !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 600 !important;
        font-size: 2.2rem !important;
        letter-spacing: -0.03em;
    }
    .title-container p {
        color: #86868b;
        font-size: 0.95rem;
    }

    /* 3. 苹果高级感：拟物化磨砂玻璃大卡片 */
    .apple-card {
        background: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(25px) saturate(190%) !important;
        -webkit-backdrop-filter: blur(25px) saturate(190%) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.06), 
                    inset 0 1px 1px 0 rgba(255, 255, 255, 0.3) !important;
        padding: 2.5rem !important;
        margin: 0 auto !important;
        max-width: 1100px !important;
        flex-grow: 0;
    }

    /* 4. 下方数据预览区卡片（等宽、限高、内部自带舒适的滚动条） */
    .result-container {
        display: flex;
        gap: 20px;
        max-width: 1200px;
        margin: 0 auto !important;
        width: 100%;
        height: 38vh !important; /* 锁死预览区高度，确保单屏 */
        margin-bottom: 2rem !important;
    }
    .sub-card {
        flex: 1;
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        padding: 1.2rem !important;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .sub-card h3 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #1d1d1f !important;
        margin-bottom: 0.8rem !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* 5. 隐藏网页自带的自带小红线和装饰 */
    [data-testid="stDecoration"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# ==================== 顶栏：高级感主标题 ====================
st.markdown("""
    <div class="title-container">
        <h1>🔋 电池数据自动化清洗分流中心</h1>
        <p>Apple Design 风格 · 规则铁律后台锁死验证</p>
    </div>
""", unsafe_allow_html=True)

# ==================== 中间：磨砂玻璃主操控卡片 ====================
st.markdown('<div class="apple-card">', unsafe_allow_html=True)

# 布局：把拖拽和下拉选择混排在中间卡片里
col_file, col_opt1, col_opt2 = st.columns([1.8, 1, 1], gap="large")

with col_file:
    uploaded_file = st.file_uploader("请在此拖拽上传原始 Excel 表格 (.xlsx)", type=["xlsx"], label_visibility="visible")

with col_opt1:
    st.markdown("**📐 尺寸换算方案**")
    size_unit = st.selectbox("单位处理", ["换算成 CM", "保持 MM"], label_visibility="collapsed")
    size_prefix = st.checkbox("加上“长宽高”前缀", value=True)

with col_opt2:
    st.markdown("**🔋 续航数据模式**")
    range_mode = st.selectbox("数字解析", ["保留区间（如 80-100）", "只要最大值"], label_visibility="collapsed")
    range_unit = st.selectbox("单位样式", ["大写 KM", "中文 公里", "纯数字"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)
st.write("") # 喘息间距

# ==================== 下方：数据结果分流展示区 ====================
# 初始化一个空槽位，确保未上传前界面也是完好的单屏
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
                brake_reason = f"行 {idx+1} 尺寸异常: 【{size_raw}】，已强制刹车！"
                break
            try:
                d_nums = [float(d.strip()) for d in dims]
            except:
                brake_triggered = True
                brake_reason = f"行 {idx+1} 尺寸含非数字: 【{size_raw}】，已强制刹车！"
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
            
            # 渲染双排苹果小卡片
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            # 这里的 columns 配合 HTML 容器做布局
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.markdown('<div class="sub-card"><h3>📂 立式结果 (款式列已切除)</h3>', unsafe_allow_html=True)
                st.dataframe(lishi_df, use_container_width=True, height=180)
                csv_li = lishi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 下载立式 CSV", data=csv_li, file_name="立式_电池数据.csv", mime="text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with res_col2:
                st.markdown('<div class="sub-card"><h3>📂 卧式结果 (款式列已切除)</h3>', unsafe_allow_html=True)
                st.dataframe(woshi_df, use_container_width=True, height=180)
                csv_wo = woshi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 下载卧式 CSV", data=csv_wo, file_name="卧式_电池数据.csv", mime="text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"表格格式读取失败: {e}")
else:
    # 没上传文件时，占位显示一个优雅的提示框，保持整体高格调单屏
    st.markdown("""
        <div class="result-container">
            <div class="sub-card" style="text-align: center; justify-content: center; color: #86868b;">
                ✨ 期待您的数据表格... 上传后这里将瞬间解锁双表无缝分流预览与一键下载
            </div>
        </div>
    """, unsafe_allow_html=True)
