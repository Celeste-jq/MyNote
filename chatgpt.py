from transformers import AutoModel, AutoTokenizer
import streamlit as st
from streamlit_chat import message
import requests
import json

st.set_page_config(
    page_title="大模型演示平台",
)


@st.cache_resource
def get_model():
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
    model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).half().cuda()
    model = model.eval()
    return tokenizer, model


MAX_TURNS = 20
MAX_BOXES = MAX_TURNS * 2


def predict(input, role, top_p, temperature, history=None):
#     tokenizer, model = get_model()
    if history is None:
        history = []

    with container:
        messages = []
        if len(history) > 0:
            for i, (role, query, response) in enumerate(history):
                message(query, avatar_style="big-smile", key=str(i) + "_user")
                message(response, avatar_style="bottts", key=str(i))
                messages.append({"role":role, "content":query})

        message(input, avatar_style="big-smile", key=str(len(history)) + "_user")
        st.write("AI正在回复:")
        with st.empty():
            messages.append({"role":role, "content":input})
            session_key = ''
            url="https://api.openai.com/v1/chat/completions"
            post_data={
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "top_p": top_p, 
                "temperature": temperature
            }
            headers={'Content-Type': 'application/json', 'Authorization':session_key}
            return_=requests.post(url,headers=headers, data = json.dumps(post_data))
            print(return_.text)
            return_dict = json.loads(return_.text)
            response = return_dict['choices'][0]['message']['content']
            st.write(response)
            history.append([role, input, response])
            print(history)
            
    return history


container = st.container()

# create a prompt text for the text generation
prompt_text = st.text_area(label="用户命令输入",
            height = 100,
            placeholder="请在这儿输入您的命令")

role = st.sidebar.radio(
    label = 'role',
    options = ('system', 'user', 'assistant')
)

top_p = st.sidebar.slider(
    'top_p', 0.0, 1.0, 0.6, step=0.01
)
temperature = st.sidebar.slider(
    'temperature(数字越大越随机)', 0.0, 2.0, 1.00, step=0.02
)

if 'state' not in st.session_state:
    st.session_state['state'] = []

if st.button("发送", key="predict"):
    with st.spinner("chatgpt模型正在生成，请稍等........"):
        # text generation
        st.session_state["state"] = predict(prompt_text, role, top_p, temperature, st.session_state["state"])