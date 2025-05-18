import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 页面设置
st.set_page_config(
    page_title="社区共享工具屋",
    page_icon="🛠️",
    layout="centered"
)

# 初始化数据
if 'tools' not in st.session_state:
    st.session_state.tools = pd.DataFrame(columns=[
        "工具名称", "工具类型", "贡献人", "联系方式", 
        "添加时间", "状态", "借用人", "预计归还时间"
    ])
    
    # 添加示例数据
    example_data = [
        ["电钻", "电动工具", "王师傅", "13800138001", 
         datetime.now().strftime("%Y-%m-%d"), "可借用", "", ""],
        ["折叠梯", "登高工具", "李阿姨", "13900139001", 
         (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "借用中", "张先生", 
         (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")]
    ]
    for item in example_data:
        st.session_state.tools.loc[len(st.session_state.tools)] = item

# 主界面
st.title("🛠️ 社区共享工具屋")
st.write("让工具流动起来，减少资源浪费")

# 功能导航
tab1, tab2, tab3 = st.tabs(["贡献工具", "工具清单", "借用管理"])

with tab1:
    # 贡献新工具
    st.subheader("贡献新工具")
    
    with st.form("add_tool_form"):
        col1, col2 = st.columns(2)
        with col1:
            tool_name = st.text_input("工具名称*", max_chars=20)
            tool_type = st.selectbox("工具类型*", 
                                   ["手动工具", "电动工具", "园艺工具", "清洁工具", "其他"])
        with col2:
            contributor = st.text_input("贡献人*", max_chars=20)
            contact = st.text_input("联系方式*", max_chars=50,
                                  placeholder="电话/微信等")
        
        if st.form_submit_button("提交贡献"):
            if tool_name and tool_type and contributor and contact:
                new_tool = {
                    "工具名称": tool_name,
                    "工具类型": tool_type,
                    "贡献人": contributor,
                    "联系方式": contact,
                    "添加时间": datetime.now().strftime("%Y-%m-%d"),
                    "状态": "可借用",
                    "借用人": "",
                    "预计归还时间": ""
                }
                st.session_state.tools = pd.concat([
                    st.session_state.tools, 
                    pd.DataFrame([new_tool])
                ], ignore_index=True)
                st.success("工具添加成功！感谢您的贡献！")
            else:
                st.error("请填写带*的必填项")

with tab2:
    # 查看工具清单
    st.subheader("工具清单")
    
    # 筛选功能
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.selectbox("按工具类型筛选", 
                                 ["全部"] + list(st.session_state.tools["工具类型"].unique()))
    with col2:
        filter_status = st.selectbox("按状态筛选", 
                                   ["全部", "可借用", "借用中"])
    
    # 应用筛选
    filtered_tools = st.session_state.tools
    if filter_type != "全部":
        filtered_tools = filtered_tools[filtered_tools["工具类型"] == filter_type]
    if filter_status != "全部":
        filtered_tools = filtered_tools[filtered_tools["状态"] == filter_status]
    
    # 显示工具列表
    if not filtered_tools.empty:
        for idx, row in filtered_tools.iterrows():
            with st.expander(f"{row['工具名称']} ({row['工具类型']}) - {row['状态']}"):
                st.write(f"**贡献人**: {row['贡献人']}")
                st.write(f"**联系方式**: {row['联系方式']}")
                st.write(f"**添加时间**: {row['添加时间']}")
                
                if row["状态"] == "借用中":
                    st.write(f"**当前借用人**: {row['借用人']}")
                    st.write(f"**预计归还时间**: {row['预计归还时间']}")
    else:
        st.info("暂无符合条件的工具")

with tab3:
    # 借用管理
    st.subheader("借用工具")
    
    # 只显示可借用的工具
    available_tools = st.session_state.tools[st.session_state.tools["状态"] == "可借用"]
    
    if not available_tools.empty:
        selected_tool = st.selectbox(
            "选择要借用的工具",
            available_tools["工具名称"].tolist()
        )
        
        tool_info = available_tools[available_tools["工具名称"] == selected_tool].iloc[0]
        
        st.write(f"**工具类型**: {tool_info['工具类型']}")
        st.write(f"**贡献人**: {tool_info['贡献人']}")
        st.write(f"**联系方式**: {tool_info['联系方式']}")
        
        with st.form("borrow_form"):
            borrower = st.text_input("借用人姓名*", max_chars=20)
            return_date = st.date_input("预计归还时间*", 
                                      min_value=datetime.today(),
                                      max_value=datetime.today() + timedelta(days=30))
            
            if st.form_submit_button("申请借用"):
                if borrower and return_date:
                    # 更新工具状态
                    idx = st.session_state.tools[
                        (st.session_state.tools["工具名称"] == selected_tool) & 
                        (st.session_state.tools["状态"] == "可借用")
                    ].index[0]
                    
                    st.session_state.tools.at[idx, "状态"] = "借用中"
                    st.session_state.tools.at[idx, "借用人"] = borrower
                    st.session_state.tools.at[idx, "预计归还时间"] = return_date.strftime("%Y-%m-%d")
                    
                    st.success(f"成功借用 {selected_tool}！请及时联系贡献人 {tool_info['贡献人']}")
                    st.balloons()
                else:
                    st.error("请填写完整信息")
    else:
        st.info("当前没有可借用的工具")

    # 归还功能
    st.divider()
    st.subheader("归还工具")
    
    borrowed_tools = st.session_state.tools[st.session_state.tools["状态"] == "借用中"]
    
    if not borrowed_tools.empty:
        returned_tool = st.selectbox(
            "选择要归还的工具",
            borrowed_tools["工具名称"].tolist()
        )
        
        if st.button("确认归还"):
            idx = st.session_state.tools[
                (st.session_state.tools["工具名称"] == returned_tool) & 
                (st.session_state.tools["状态"] == "借用中")
            ].index[0]
            
            st.session_state.tools.at[idx, "状态"] = "可借用"
            st.session_state.tools.at[idx, "借用人"] = ""
            st.session_state.tools.at[idx, "预计归还时间"] = ""
            
            st.success(f"{returned_tool} 已成功归还！")
    else:
        st.info("当前没有借出中的工具")

# 页脚
st.divider()
st.write("""
**使用规则**:
1. 借用工具请爱惜使用
2. 按时归还以便他人使用
3. 损坏工具需照价赔偿
""")
