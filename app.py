import streamlit as st
from openai import OpenAI
import os

# 页面基础配置
st.set_page_config(page_title="Cai's AI Lab", page_icon="🧪", layout="wide")

# --- 侧边栏：高级配置 ---
with st.sidebar:
    st.title("🤖 控制中心")
    
    # 尝试从环境变量获取 Key，或者手动输入
    default_key = os.getenv("OPENAI_API_KEY", "")
    api_key = st.text_input("OpenAI API Key", value=default_key, type="password")
    
    st.divider()
    
    # 角色切换器 (System Prompt)
    role_type = st.selectbox("当前助手角色", ["通用助手", "电影导演/编剧", "Prompt 优化专家", "技术专家"])
    
    roles = {
        "通用助手": "你是一个全能助手。",
        "电影导演/编剧": "你是一位资深电影导演，擅长镜头语言分析、剧本结构及视觉叙事。",
        "Prompt 优化专家": "你是一个 Midjourney 和 AIGC 提示词专家，擅长将模糊的想法转化为精准的参数化指令。",
        "技术专家": "你是一个精通 Python 和 Streamlit 的前端与 AI 开发者。"
    }
    
    st.divider()
    
    # 参数微调
    model_choice = st.selectbox("模型选择", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
    temp = st.slider("Temperature (创造力)", 0.0, 1.5, 0.7, 0.1)
    
    if st.button("🗑️ 清空当前对话"):
        st.session_state.messages = []
        st.rerun()

# --- 对话核心逻辑 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 输入处理
if prompt := st.chat_input("输入你的指令..."):
    if not api_key:
        st.warning("请输入 API Key 以继续")
        st.stop()

    client = OpenAI(api_key=api_key)
    
    # 记录用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 构造请求消息组 (包含 System Prompt)
    api_messages = [{"role": "system", "content": roles[role_type]}]
    api_messages.extend([
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ])

    # AI 流式流式输出
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=model_choice,
                messages=api_messages,
                temperature=temp,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            
            # 记录 AI 回复
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
