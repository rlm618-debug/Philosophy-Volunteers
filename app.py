import streamlit as st
import uuid
import datetime
import json
import requests
import base64

# --- 1. 配置 ---
st.set_page_config(page_title="Philograph 哲学协作平台", layout="wide")

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "rlm618-debug/Philosophy-Volunteers"
FILE_PATH = "philosophy_db.json"

# --- 2. GitHub 同步逻辑 ---
def get_github_data():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        res = r.json()
        content = base64.b64decode(res['content']).decode('utf-8')
        return json.loads(content), res['sha']
    return [], None

def save_to_github(data, sha):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content_base64 = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"Update Philograph data: {datetime.datetime.now()}",
        "content": content_base64,
        "sha": sha
    }
    r = requests.put(url, json=payload, headers=headers)
    return r.status_code

# 启动时初始化
if 'tasks' not in st.session_state:
    data, sha = get_github_data()
    st.session_state.tasks = data
    st.session_state.db_sha = sha

# --- 3. 侧边栏 ---
with st.sidebar:
    st.title("📖 站点指南")
    if 'user' not in st.session_state:
        st.warning("⚠️ 请先开启身份以解锁功能。")
        if st.button("🚀 开启研究员身份", use_container_width=True):
            st.session_state.user = "研究员_" + uuid.uuid4().hex[:4]
            st.rerun()
    else:
        st.success(f"当前身份: {st.session_state.user}")
        if st.button("退出登录"):
            del st.session_state.user
            st.rerun()

    st.divider()
    st.subheader("🤝 合作与致谢")
    st.info("我对本项目不要求任何所有权和个人利益。欢迎联系我：[yourname@email.com]")

# --- 4. 发布命题 ---
st.title("📜 Philograph: 论证协作平台")

if 'user' in st.session_state:
    with st.expander("➕ 启动新论证任务"):
        content = st.text_area("输入论证命题...")
        if st.button("发布命题"):
            if content:
                new_task = {
                    "id": str(uuid.uuid4())[:8].upper(),
                    "author": st.session_state.user,
                    "content": content,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "replies": []
                }
                data, sha = get_github_data()
                data.append(new_task)
                save_to_github(data, sha)
                st.session_state.tasks = data
                st.success("命题已存入 GitHub 存档！")
                st.rerun()
else:
    st.info("💡 请在左侧开启身份，参与哲学论证。")

# --- 5. 论证展示、回答与评价 ---
st.subheader("🌐 论证大厅")

for i, task in enumerate(reversed(st.session_state.tasks)):
    orig_idx = len(st.session_state.tasks) - 1 - i
    with st.container(border=True):
        st.markdown(f"### 📍 ID: `{task['id']}`")
        st.info(task['content'])
        st.caption(f"发起者: {task['author']} | 时间: {task['time']}")
        
        # 展示已有的回答
        if task.get('replies'):
            for r_idx, reply in enumerate(task['replies']):
                with st.chat_message("user"):
                    st.write(f"**{reply['author']}** 的回答：")
                    st.write(reply['content'])
                    
                    # 展示评价
                    for eval_text in reply.get('evaluations', []):
                        st.caption(f"🧐 {eval_text}")
                    
                    # 评价输入
                    if 'user' in st.session_state:
                        with st.popover("评价此回答"):
                            e_input = st.text_input("输入评析...", key=f"e_{task['id']}_{r_idx}")
                            if st.button("提交评价", key=f"eb_{task['id']}_{r_idx}"):
                                data, sha = get_github_data()
                                # 找到对应任务和回答
                                for t in data:
                                    if t['id'] == task['id']:
                                        if 'evaluations' not in t['replies'][r_idx]:
                                            t['replies'][r_idx]['evaluations'] = []
                                        t['replies'][r_idx]['evaluations'].append(f"{st.session_state.user}: {e_input}")
                                        break
                                save_to_github(data, sha)
                                st.session_state.tasks = data
                                st.rerun()

        # 提交新回答
        if 'user' in st.session_state:
            with st.expander("✍️ 提交我的回答"):
                r_content = st.text_area("输入你的逻辑论证...", key=f"ra_{task['id']}")
                if st.button("提交回答", key=f"rb_{task['id']}"):
                    data, sha = get_github_data()
                    for t in data:
                        if t['id'] == task['id']:
                            t['replies'].append({
                                "author": st.session_state.user,
                                "content": r_content,
                                "evaluations": []
                            })
                            break
                    save_to_github(data, sha)
                    st.session_state.tasks = data
                    st.rerun()
