import streamlit as st
import uuid
import datetime
import json
import requests
import base64

# --- 1. 基础配置 ---
st.set_page_config(page_title="Philograph | 哲学协作平台", layout="wide")

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "rlm618-debug/Philosophy-Volunteers"
FILE_PATH = "philosophy_db.json"

# --- 2. 双语词典 ---
LANG = {
    "CN": {
        "title": "📜 Philograph: 论证协作平台",
        "sidebar_guide": "📖 站点指南",
        "login_btn": "🚀 开启研究员身份",
        "logout_btn": "退出登录",
        "identity_prefix": "当前身份: ",
        "login_warn": "⚠️ 请先开启身份以解锁功能。",
        "how_to": "**如何参与：**\n1. **发布**：提出哲学命题。\n2. **回答**：提交逻辑拆解。\n3. **评价**：进行深度评析。",
        "collab": "🤝 合作与致谢",
        "collab_text": "我对本项目不要求所有权。欢迎联系我：[rlm618@york.ac.uk]",
        "new_task": "➕ 启动新论证任务",
        "input_label": "输入论证命题...",
        "pub_btn": "发布命题",
        "pub_success": "命题已存入 GitHub 存档！",
        "hall": "🌐 论证大厅",
        "no_data": "目前档案库为空。",
        "author": "发起者",
        "time": "时间",
        "reply_btn": "✍️ 提交我的回答",
        "eval_btn": "评价此回答",
        "eval_label": "输入评析...",
        "submit_eval": "提交评价",
        "submit_reply": "提交回答",
        "reply_placeholder": "输入你的逻辑论证...",
        "login_info": "💡 请在左侧开启身份，参与哲学论证。"
    },
    "EN": {
        "title": "📜 Philograph: Argument Collaboration",
        "sidebar_guide": "📖 Guide",
        "login_btn": "🚀 Start Researcher Identity",
        "logout_btn": "Logout",
        "identity_prefix": "Current User: ",
        "login_warn": "⚠️ Please start identity to unlock features.",
        "how_to": "**How to participate:**\n1. **Post**: Propose a proposition.\n2. **Reply**: Submit logical deconstruction.\n3. **Evaluate**: Provide deep analysis.",
        "collab": "🤝 Collaboration",
        "collab_text": "I claim no ownership. Contact me: [yourname@email.com]",
        "new_task": "➕ Start New Task",
        "input_label": "Enter proposition...",
        "pub_btn": "Post Proposition",
        "pub_success": "Archived to GitHub!",
        "hall": "🌐 Lobby",
        "no_data": "No tasks yet.",
        "author": "Author",
        "time": "Time",
        "reply_btn": "✍️ Submit My Reply",
        "eval_btn": "Evaluate Reply",
        "eval_label": "Enter analysis...",
        "submit_eval": "Submit Evaluation",
        "submit_reply": "Submit Reply",
        "reply_placeholder": "Enter your logical argument...",
        "login_info": "💡 Please start identity on the left to participate."
    }
}

# --- 3. GitHub 同步逻辑 ---
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
    payload = {"message": f"Update: {datetime.datetime.now()}", "content": content_base64, "sha": sha}
    requests.put(url, json=payload, headers=headers)

if 'tasks' not in st.session_state:
    data, sha = get_github_data()
    st.session_state.tasks = data
    st.session_state.db_sha = sha

# --- 4. 侧边栏 ---
with st.sidebar:
    # 语言切换器
    lang_choice = st.radio("🌐 Language / 语言", ["中文", "English"], horizontal=True)
    L = LANG["CN"] if lang_choice == "中文" else LANG["EN"]
    
    st.title(L["sidebar_guide"])
    if 'user' not in st.session_state:
        st.warning(L["login_warn"])
        if st.button(L["login_btn"], use_container_width=True):
            st.session_state.user = "Res_" + uuid.uuid4().hex[:4]
            st.rerun()
    else:
        st.success(f"{L['identity_prefix']} {st.session_state.user}")
        if st.button(L["logout_btn"]):
            del st.session_state.user
            st.rerun()

    st.markdown(L["how_to"])
    st.divider()
    st.subheader(L["collab"])
    st.info(L["collab_text"])

# --- 5. 主界面 ---
st.title(L["title"])

if 'user' in st.session_state:
    with st.expander(L["new_task"]):
        content = st.text_area(L["input_label"])
        if st.button(L["pub_btn"]):
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
                st.success(L["pub_success"])
                st.rerun()
else:
    st.info(L["login_info"])

st.subheader(L["hall"])
if not st.session_state.tasks:
    st.write(L["no_data"])

for i, task in enumerate(reversed(st.session_state.tasks)):
    orig_idx = len(st.session_state.tasks) - 1 - i
    with st.container(border=True):
        st.markdown(f"### 📍 ID: `{task['id']}`")
        st.info(task['content'])
        st.caption(f"{L['author']}: {task['author']} | {L['time']}: {task['time']}")
        
        if task.get('replies'):
            for r_idx, reply in enumerate(task['replies']):
                with st.chat_message("user"):
                    st.write(f"**{reply['author']}**:")
                    st.write(reply['content'])
                    for eval_text in reply.get('evaluations', []):
                        st.caption(f"🧐 {eval_text}")
                    if 'user' in st.session_state:
                        with st.popover(L["eval_btn"]):
                            e_input = st.text_input(L["eval_label"], key=f"e_{task['id']}_{r_idx}")
                            if st.button(L["submit_eval"], key=f"eb_{task['id']}_{r_idx}"):
                                data, sha = get_github_data()
                                for t in data:
                                    if t['id'] == task['id']:
                                        if 'evaluations' not in t['replies'][r_idx]: t['replies'][r_idx]['evaluations'] = []
                                        t['replies'][r_idx]['evaluations'].append(f"{st.session_state.user}: {e_input}")
                                        break
                                save_to_github(data, sha)
                                st.session_state.tasks = data
                                st.rerun()

        if 'user' in st.session_state:
            with st.expander(L["reply_btn"]):
                r_content = st.text_area(L["reply_placeholder"], key=f"ra_{task['id']}")
                if st.button(L["submit_reply"], key=f"rb_{task['id']}"):
                    data, sha = get_github_data()
                    for t in data:
                        if t['id'] == task['id']:
                            t['replies'].append({"author": st.session_state.user, "content": r_content, "evaluations": []})
                            break
                    save_to_github(data, sha)
                    st.session_state.tasks = data
                    st.rerun()
