import streamlit as st
import uuid
import datetime

# --- 页面设置 ---
st.set_page_config(page_title="Philograph 哲学协作平台", layout="wide")

# --- 数据初始化 ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False

# --- 侧边栏 ---
with st.sidebar:
    st.title("👤 用户中心")
    if not st.session_state.is_logged_in:
        if st.button("模拟登录"):
            st.session_state.is_logged_in = True
            st.session_state.user = "研究员_" + uuid.uuid4().hex[:4]
            st.rerun()
    else:
        st.success(f"已登录: {st.session_state.user}")
        if st.button("退出登录"):
            st.session_state.is_logged_in = False
            st.rerun()

# --- 主界面 ---
st.title("📜 Philograph: 哲学论证协作平台")
st.write("欢迎来到哲学论证存证系统。在这里，每一个逻辑节点都拥有唯一的身份 ID。")

# 1. 发布任务
if st.session_state.is_logged_in:
    with st.expander("➕ 发布新的哲学命题/任务"):
        content = st.text_area("输入论证内容...", placeholder="例如：苏格拉底的‘精神助产术’在AI时代是否依然有效？")
        if st.button("提交并铸造 ID"):
            new_id = f"PHIL-2026-{uuid.uuid4().hex[:4].upper()}"
            st.session_state.tasks.append({
                "id": new_id,
                "author": st.session_state.user,
                "content": content,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"发布成功！任务 ID: {new_id}")

# 2. 任务列表
st.subheader("🌐 任务大厅")
if not st.session_state.tasks:
    st.info("目前还没有发布的任务。")
else:
    for task in reversed(st.session_state.tasks):
        with st.container(border=True):
            st.write(f"**ID:** `{task['id']}`")
            st.info(task['content'])
            st.caption(f"✍️ 贡献者: {task['author']}  |  ⏰ 时间: {task['time']}")
