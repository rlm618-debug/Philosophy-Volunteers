import streamlit as st
import uuid
import datetime
import json
import requests
import base64

# --- 1. 配置（保持不变） ---
st.set_page_config(page_title="Philograph 哲学协作平台", layout="wide")

# --- 2. 核心：GitHub 自动存取逻辑 ---
# 这里的配置会从 Streamlit 的 Secrets 里读取（稍后我会教你怎么填 Secrets）
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "rlm618-debug/Philosophy-Volunteers"
FILE_PATH = "philosophy_db.json"

def get_github_data():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = base64.b64decode(r.json()['content']).decode('utf-8')
        return json.loads(content), r.json()['sha']
    return [], None

def save_to_github(data, sha):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content_base64 = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8')).decode('utf-8')
    payload = {
        "message": "Update database via Streamlit",
        "content": content_base64,
        "sha": sha
    }
    requests.put(url, json=payload, headers=headers)

# 启动时读取一次
if 'tasks' not in st.session_state:
    data, sha = get_github_data()
    st.session_state.tasks = data
    st.session_state.db_sha = sha

# --- 3. 侧边栏与主界面（与之前逻辑一致，仅增加了自动保存触发） ---
with st.sidebar:
    st.title("📖 站点指南")
    if 'user' not in st.session_state:
        st.warning("⚠️ 请先开启身份。")
        if st.button("🚀 开启研究员身份"):
            st.session_state.user = "研究员_" + uuid.uuid4().hex[:4]
            st.rerun()
    else:
        st.success(f"当前身份: {st.session_state.user}")
    
    st.divider()
    st.info("💡 你的所有贡献都会自动存档至 GitHub 仓库。")

# --- 4. 发布与展示逻辑 ---
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
                # 更新并同步到 GitHub
                current_data, current_sha = get_github_data()
                current_data.append(new_task)
                save_to_github(current_data, current_sha)
                st.session_state.tasks = current_data
                st.success("命题已永久存档！")
                st.rerun()

# 展示大厅（同之前...）
for i, task in enumerate(reversed(st.session_state.tasks)):
    with st.container(border=True):
        st.markdown(f"### 📍 ID: `{task['id']}`")
        st.info(task['content'])
        # 回答与评价的保存逻辑也只需在提交处调用 save_to_github 即可
        # (篇幅有限，此处仅展示核心发布存档逻辑)
