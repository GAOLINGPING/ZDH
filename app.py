import streamlit as st
import pandas as pd
import re
import base64

# 设置页面基本配置
st.set_page_config(page_title="电池数据自动化处理助手", layout="wide")

st.title("🔋 电池数据自动化清洗分流中心")
st.caption("第一版核心稳定版：导入原始表格后，自动完成逻辑清洗并提供一键分流下载")

# ==================== 顶层控制面板 ====================
with st.container():
    col_file, col_opt1, col_opt2 = st.columns([1.5, 1, 1], gap="medium")
    
    with col_file:
        st.subheader("1. 上传原始文件")
        uploaded_file = st.file_uploader("请选择或拖拽 Excel 表格 (.xlsx)", type=["xlsx"])

    with col_opt1:
        st.subheader("2. 尺寸单位配置")
        size_unit = st.selectbox("单位转换选择", ["保持 MM", "换算成 CM"])
        size_prefix = st.checkbox("增加“长宽高”汉字前缀", value=True)

    with col_opt2:
        st.subheader("3. 续航里程配置")
        range_mode = st.selectbox("数字过滤模式", ["保留区间（如 80-100）", "只要最大值"])
        range_unit = st.selectbox("后缀单位选择", ["大写 KM", "中文 公里", "纯数字"])

st.markdown("---")

# ==================== 核心逻辑处理函数 ====================
def to_csv_download_link(df, filename, button_text):
    """生成无乱码的 CSV 一键下载链接按钮"""
    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv_data.encode('utf-8-sig')).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background-color:#00c853; color:white; border:none; padding:10px 20px; font-weight:bold; border-radius:5px; cursor:pointer;">{button_text}</button></a>'

# ==================== 自动化处理引擎 ====================
if uploaded_file:
    try:
        # 读取 Excel，不设表头以便精准按坐标处理
        df = pd.read_excel(uploaded_file, header=None)
        
        # 核心铁律：前三列合并单元格向下填充
        df[0] = df[0].ffill()
        df[1] = df[1].ffill()
        df[2] = df[2].ffill()
        
        # 从第 4 行开始（索引3）切片提取实际数据
        data_rows = df.iloc[3:].copy()
        cleaned_data = []
        
        brake_triggered = False
        brake_reason = ""

        for idx, row in data_rows.iterrows():
            # 过滤行：只保留立式和卧式
            style = str(row[2]).strip()
            if style not in ['立式', '卧式']:
                continue
                
            # 获取 SKU 信息列进行文本解析
            sku_text = str(row[9]).strip() if pd.notna(row[9]) else ""
            
            # --- 1. 规格提取 ---
            v_raw = str(row[1]).strip().upper()
            v_str = v_raw if "V" in v_raw else (v_raw + "V" if v_raw.isdigit() else "未知V")
            if v_str == "未知V":
                v_m = re.search(r'(\d+)\s*V', sku_text, re.IGNORECASE)
                if v_m:
                    v_str = v_m.group(1) + "V"

            ah_m = re.search(r'(\d+)\s*AH', sku_text, re.IGNORECASE)
            if not ah_m:
                ah_m = re.search(r'(\d+)\s*A(?!M)', sku_text, re.IGNORECASE)
            if not ah_m:
                ah_m = re.search(r'\d+\s*[vV]\s*(\d+)', sku_text)
            ah_str = ah_m.group(1) + "AH" if ah_m else "未知AH"
            
            spec = f"{v_str}{ah_str}"
            
            # --- 2. 尺寸提取与安全刹车 ---
            size_raw = str(row[3]).strip()
            dims = re.split(r'[*xX×]', size_raw)
            
            if len(dims) != 3 or size_raw.isdigit():
                brake_triggered = True
                brake_reason = f"第 {idx+1} 行尺寸异常: 【{size_raw}】，触发安全刹车！请检查数据。"
                break
            try:
                d_nums = [float(d.strip()) for d in dims]
            except:
                brake_triggered = True
                brake_reason = f"第 {idx+1} 行尺寸包含非法非数字字符: 【{size_raw}】，触发安全刹车！"
                break
                
            # 单位转换与去小数点
            if size_unit == "换算成 CM":
                d_nums = [n / 10 for n in d_nums]
                d_strs = [str(int(n)) if n.is_integer() else str(n) for n in d_nums]
                unit_label = "CM"
            else:
                d_strs = [str(int(n)) if n.is_integer() else str(n) for n in d_nums]
                unit_label = "MM"
                
            # 是否加汉字前缀
            if size_prefix:
                l_str, w_str, h_str = f"长{d_strs[0]}{unit_label}", f"宽{d_strs[1]}{unit_label}", f"高{d_strs[2]}{unit_label}"
            else:
                l_str, w_str, h_str = f"{d_strs[0]}{unit_label}", f"{d_strs[1]}{unit_label}", f"{d_strs[2]}{unit_label}"
                
            # --- 3. 续航解析 ---
            range_m = re.search(r'([\d\-]+)\s*km', sku_text, re.IGNORECASE)
            if not range_m:
                range_m = re.search(r'([\d\-]+)\s*公里', sku_text)
            
            if range_m:
                raw_val = range_m.group(1)
                if range_mode == "只要最大值" and "-" in raw_val:
                    final_num = raw_val.split("-")[-1].strip()
                else:
                    final_num = raw_val
            else:
                final_num = "未知"
                
            u_suffix = "" if range_unit == "纯数字" else ("KM" if range_unit == "大写 KM" else "公里")
            range_final = f"{final_num}{u_suffix}" if final_num != "未知" else "未知"
            
            # --- 4. 蓝牙判断 ---
            is_bluetooth = "TRUE" if "蓝牙" in sku_text or "蓝牙" in str(row[5]) else "FALSE"
            
            # 整合单行洗净数据
            cleaned_data.append({
                "电池规格": spec,
                "款式": style,
                "长": l_str,
                "宽": w_str,
                "高": h_str,
                "续航": range_final,
                "蓝牙": is_bluetooth
            })
            
        # 安全刹车检查与结果呈现
        if brake_triggered:
            st.error(f"🛑 处理中止：{brake_reason}")
        else:
            # 转换为 DataFrame 并按款式拆分分流
            res_df = pd.DataFrame(cleaned_data)
            lishi_df = res_df[res_df['款式'] == '立式'].drop(columns=['款式'])
            woshi_df = res_df[res_df['款式'] == '卧式'].drop(columns=['款式'])
            
            st.success("🎉 数据清洗成功！已自动按款式完成数据分流：")
            
            # 左右双栏展示清洗后的最终大盘与下载按钮
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.subheader("📊 立式电池结果")
                st.dataframe(lishi_df, use_container_width=True)
                download_link_li = to_csv_download_link(lishi_df, "立式_电池清洗数据.csv", "📥 导出立式表格 (.csv)")
                st.markdown(download_link_li, unsafe_allow_html=True)
                
            with res_col2:
                st.subheader("📊 卧式电池结果")
                st.dataframe(woshi_df, use_container_width=True)
                download_link_wo = to_csv_download_link(woshi_df, "卧式_电池清洗数据.csv", "📥 导出卧式表格 (.csv)")
                st.markdown(download_link_wo, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"出现未知错误，请检查表格结构是否符合规范。错误详情: {e}")
else:
    st.info("💡 提示：请在上方控制台上传您的电池原始 Excel 文件开始
