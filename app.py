import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="电池数据自动化清洗分流工具", layout="wide", initial_sidebar_state="expanded")

# 界面标题
st.title("🔋 电池数据自动化清洗分流工具")
st.caption("老大专属定制版 - 严格执行全套数据铁律，数据百分百高度可控")
st.write("---")

# ================= 1. 侧边栏：开跑前的格式皮肤勾选 =================
st.sidebar.header("📐 尺寸格式配置")
size_unit = st.sidebar.selectbox("尺寸单位换算", ["保持 MM", "换算成 CM"])
size_prefix = st.sidebar.checkbox("带“长宽高”汉字前缀", value=True)

st.sidebar.write("---")
st.sidebar.header("🔋 续航格式配置")
range_mode = st.sidebar.selectbox("数字提取模式", ["保留区间（如 80-100）", "只要最大值（如 100）"])
range_unit = st.sidebar.selectbox("续航单位选择", ["大写 KM", "中文 公里", "纯数字（无单位）"])
range_prefix_opt = st.sidebar.selectbox("修饰前缀", ["无前缀", "加“续航”", "加“参考”", "加“约”"])

# ================= 2. 主界面：文件拖拽上传 =================
uploaded_file = st.file_uploader("请拖拽或选择你要清洗的 Excel 文件 (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # 读取 Excel，不设表头
        df = pd.read_excel(uploaded_file, header=None)
        
        # 铁律：向下填充前三列合并单元格（电芯、电压、款式）
        df[0] = df[0].ffill()
        df[1] = df[1].ffill()
        df[2] = df[2].ffill()
        
        # 数据行从第4行（索引3）开始
        data_rows = df.iloc[3:].copy()
        cleaned_data = []
        brake_triggered = False
        brake_reason = ""

        for idx, row in data_rows.iterrows():
            style = str(row[2]).strip()
            # 过滤掉非立式、卧式的杂行
            if style not in ['立式', '卧式']:
                continue
                
            sku_text = str(row[9]).strip() if pd.notna(row[9]) else ""
            
            # --- 🔋 电池规格提取与纠错 (第一列锁死) ---
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
            
            # --- 📐 尺寸处理（触发异常刹车机制） ---
            size_raw = str(row[3]).strip()
            dims = re.split(r'[*xX×]', size_raw)
            
            # 刹车机制：只要不是标准长宽高3项，或是空数字，直接抛出异常
            if len(dims) != 3 or size_raw.isdigit():
                brake_triggered = True
                brake_reason = f"行 {idx+1} 尺寸数据残缺、不规范或为纯裸数字: 【{size_raw}】，触发安全刹车！"
                break
                
            try:
                d_nums = [float(d.strip()) for d in dims]
            except:
                brake_triggered = True
                brake_reason = f"行 {idx+1} 尺寸含有无法解析的非数字内容: 【{size_raw}】，触发安全刹车！"
                break
                
            # 单位换算与去.0逻辑
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
                
            # --- 🔋 续航处理 ---
            range_m = re.search(r'([\d\-]+)\s*km', sku_text, re.IGNORECASE)
            if not range_m: range_m = re.search(r'([\d\-]+)\s*公里', sku_text)
            
            if range_m:
                raw_val = range_m.group(1)
                if "-" in raw_val and range_mode == "只要最大值（如 100）":
                    final_num = raw_val.split("-")[-1].strip()
                else:
                    final_num = raw_val
            else:
                final_num = "未知"
                
            u_suffix = "" if range_unit == "纯数字（无单位）" else ("KM" if range_unit == "大写 KM" else "公里")
            p_prefix = "" if range_prefix_opt == "无前缀" else (range_prefix_opt.replace("加“", "").replace("”", ""))
            
            range_final = f"{p_prefix}{final_num}{u_suffix}" if final_num != "未知" else "未知"
            
            # --- 📱 蓝牙智能处理 ---
            is_bluetooth = "TRUE" if "蓝牙" in sku_text or "蓝牙" in str(row[5]) else "FALSE"
            
            # 装配规范字典（款式仅作在后台分流用）
            cleaned_data.append({
                "电池规格": spec,
                "款式": style,
                "长": l_str,
                "宽": w_str,
                "高": h_str,
                "续航": range_final,
                "蓝牙": is_bluetooth
            })
            
        # ================= 3. 结果渲染与分表下载 =================
        if brake_triggered:
            st.error(f"🛑 发现错误：{brake_reason}")
            st.warning("请先去原始 Excel 表里修正该行数据，然后再重新上传。")
        else:
            # 转换为 DataFrame
            res_df = pd.DataFrame(cleaned_data)
            
            # 物理分流，并彻底剔除【款式】那一列
            lishi_df = res_df[res_df['款式'] == '立式'].drop(columns=['款式'])
            woshi_df = res_df[res_df['款式'] == '卧式'].drop(columns=['款式'])
            
            st.success("🎉 数据全部清洗完毕！已严格按照您勾选的皮肤自动拼装。")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📂 立式电池结果 (款式列已剔除)")
                st.dataframe(lishi_df)
                csv_li = lishi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 下载《立式_电池数据.csv》", data=csv_li, file_name="立式_电池数据.csv", mime="text/csv")
                
            with col2:
                st.subheader("📂 卧式电池结果 (款式列已剔除)")
                st.dataframe(woshi_df)
                csv_wo = woshi_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 下载《卧式_电池数据.csv》", data=csv_wo, file_name="卧式_电池数据.csv", mime="text/csv")
                
    except Exception as e:
        st.error(f"导入表格失败，请确认表格结构是否被改动。报错信息: {e}")