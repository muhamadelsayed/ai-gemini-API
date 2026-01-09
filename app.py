import streamlit as st
import google.generativeai as genai
import json
import os
import glob

# إعدادات المجلدات
CHATS_DIR = "my_chats"
if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR)

# وظائف المساعدة
def get_chat_files():
    files = glob.glob(os.path.join(CHATS_DIR, "*.json"))
    return [os.path.basename(f).replace(".json", "") for f in files]

def save_chat(chat_name, messages):
    file_path = os.path.join(CHATS_DIR, f"{chat_name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_chat(chat_name):
    file_path = os.path.join(CHATS_DIR, f"{chat_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# تحويل الرسائل لتنسيق Gemini الرسمي (لحل مشكلة KeyError)
def format_for_gemini(messages):
    formatted = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        formatted.append({"role": role, "parts": [{"text": m["content"]}]})
    return formatted

st.set_page_config(page_title="Gemini Pro Studio", layout="wide")
st.title("🚀 Gemini Advanced Interface")

with st.sidebar:
    st.header("🔑 الإعدادات")
    api_key = st.text_input("API Key:", type="password")
    
    st.divider()
    st.header("💬 المحادثات")
    existing_chats = get_chat_files()
    selected_chat = st.selectbox("اختر محادثة:", [""] + existing_chats)
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            if "models_list" not in st.session_state:
                st.session_state.models_list = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model_choice = st.selectbox("النموذج:", st.session_state.models_list)
        except:
            st.error("تأكد من الـ API Key")

# منطق المحادثة
if api_key and selected_chat:
    model = genai.GenerativeModel(model_name=f"models/{model_choice}")
    
    # تحميل المحادثة
    if "messages" not in st.session_state or st.session_state.get("last_chat") != selected_chat:
        st.session_state.messages = load_chat(selected_chat)
        st.session_state.last_chat = selected_chat
        st.session_state.view_limit = 10 # الافتراضي عرض آخر 10

    # زر تحميل المزيد
    if len(st.session_state.messages) > st.session_state.view_limit:
        if st.button("🔽 تحميل رسائل أقدم"):
            st.session_state.view_limit += 10
            st.rerun()

    # عرض الرسائل (بناءً على الليميت المختار)
    display_msgs = st.session_state.messages[-st.session_state.view_limit:]
    for m in display_msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # الإرسال
    if prompt := st.chat_input("اكتب سؤالك هنا..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # تحسين: إرسال آخر 10 رسائل فقط للموديل لتجنب خطأ 429 و 404
        # الـ history يحتاج لتنسيق 'parts'
        history_to_send = format_for_gemini(st.session_state.messages[-11:-1])
        
        chat = model.start_chat(history=history_to_send)
        
        try:
            with st.spinner("جاري التفكير..."):
                response = chat.send_message(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            save_chat(selected_chat, st.session_state.messages)
            
            # حساب التوكنز بشكل صحيح (إصلاح KeyError)
            formatted_history = format_for_gemini(st.session_state.messages)
            tokens = model.count_tokens(formatted_history).total_tokens
            st.sidebar.metric("إجمالي التوكنز في الملف", tokens)
            
        except Exception as e:
            st.error(f"خطأ: {e}")

elif not selected_chat:
    st.info("اختر محادثة من القائمة الجانبية للبدء.")