import streamlit as st
import uuid
import datetime
import json
import os

# --- 1. 基础配置 ---
st.set_page_config(page_title="Philograph 2.0", layout="wide")

# --- 2. 模拟数据库 (简单文件存储) ---
# 这会让内容在一定程度上“留存”，即使刷新网页也可能还在（取决于服务器重启频率）
DB_FILE = "philosophy_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'tasks' not in st.session_state:
    st.session_state.tasks = load_data()

# --- 3. 侧边栏：用户说明 ---
with st.sidebar:
    st.title("📖 使用说明")
    st.markdown("""
    **欢迎来到 Philograph！**
    这里是哲学志愿者的论证协作空间：
    1. **登录**：点击下方按钮获取研究员编号。
    2. **发布**：提出一个待论证的哲学命题。
    3. **回答**：对现有命题提交你的逻辑拆解。
    4. **评价**：对参与者的回答进行深度评析。
    ---
    *注：当前为测试版，数据存储在临时云端。*
    """)
    
    if not st.get_option("client.showErrorDetails"): # 仅作界面美化
        st.divider()
        
    if 'user' not in st.session_state:
        if st.button("🚀 开启研究员身份"):
            st.session_state.user = "研究员_" + uuid.uuid4().hex[:4]
            st.rerun()
    else:
        st.success(f"当前身份: {st.session_state.user}")

# --- 4. 主界面 ---
st.title("📜 Philograph: 论证协作平台")

# 发布功能
if 'user' in st.session_state:
    with st.expander("➕ 启动新论证任务"):
        content = st.text_area("输入论证命题...")
        if st.button("发布命题"):
            new_task = {
                "id": str(uuid.uuid4())[:8],
                "author": st.session_state.user,
                "content": content,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "replies": []
            }
            st.session_state.tasks.append(new_task)
            save_data(st.session_state.tasks)
            st.success("命题已存入档案！")
            st.rerun()

# --- 5. 任务展示与交互 (问题-回答-评价) ---
st.subheader("🌐 论证大厅")

for i, task in enumerate(reversed(st.session_state.tasks)):
    idx = len(st.session_state.tasks) - 1 - i
    with st.container(border=True):
        st.markdown(f"### 📍 命题 ID: `{task['id']}`")
        st.info(task['content'])
        st.caption(f"发布者: {task['author']} | 时间: {task['time']}")
        
        # 回答展示区
        if task['replies']:
            st.markdown("---")
            for r_idx, reply in enumerate(task['replies']):
                st.write(f"💬 **{reply['author']}** 的回答:")
                st.write(reply['content'])
                # 展示对回答的评价
                for eval_text in reply.get('evaluations', []):
                    st.warning(f"🧐 评价: {eval_text}")
                
                # 评价输入框
                if 'user' in st.session_state:
                    eval_input = st.text_input(f"评价该回答", key=f"eval_{task['id']}_{r_idx}")
                    if st.button("提交评价", key=f"btn_eval_{task['id']}_{r_idx}"):
                        if 'evaluations' not in reply: reply['evaluations'] = []
                        reply['evaluations'].append(f"{st.session_state.user}: {eval_input}")
                        save_data(st.session_state.tasks)
                        st.rerun()
                st.write("")

        # 回答输入框
        if 'user' in st.session_state:
            with st.expander("✍️ 我来回答"):
                reply_content = st.text_area("输入你的逻辑论证...", key=f"reply_area_{task['id']}")
                if st.button("提交回答", key=f"reply_btn_{task['id']}"):
                    st.session_state.tasks[idx]['replies'].append({
                        "author": st.session_state.user,
                        "content": reply_content,
                        "evaluations": []
                    })
                    save_data(st.session_state.tasks)
                    st.rerun()

if not st.session_state.tasks:
    st.write("目前档案库为空。")
