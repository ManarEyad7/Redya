import streamlit as st
import os
import getpass
from ibm_watsonx_ai.foundation_models import Model

# Function to get credentials for IBM Watsonx
def get_credentials():
    return {
        "url": "https://eu-de.ml.cloud.ibm.com",
        "apikey": "PxrEtdAhNUfC4zNk7haVaFiF95fczhvNFj_ghIWGxDFu"
    }

# Watsonx model initialization
def initialize_model():
    model_id = "sdaia/allam-1-13b-instruct"
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 900,
        "repetition_penalty": 1
    }
    project_id = "0c239eae-c65e-4108-8601-d8fff1e102ea"

    model = Model(
        model_id=model_id,
        params=parameters,
        credentials=get_credentials(),
        project_id=project_id
    )
    return model

# Initialize the model once when the app starts
model = initialize_model()

# Define prompt template
prompt_input = """<<SYS>>
انت شاعر قم بممارسة المحاورة الشعرية مع اتباع القواعد التالية :
الوزن: حافظ على وزن البحر الشعري المستخدم في الأبيات ...
... يجب بعد الرد ذكر وزن البيت والقافية 
<</SYS>>
"""

def get_watsonx_response(question):
    formatted_question = f"""<s> [INST] {question} [/INST]"""
    prompt = f"{prompt_input}{formatted_question}"
    generated_response = model.generate_text(prompt=prompt, guardrails=False)
    return generated_response

# Apply CSS to make the interface RTL (right-to-left)
st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
    }
    .css-1v3fvcr {
        direction: rtl;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# عنوان الصفحة
st.title("رديّة - محاورة شعرية")
st.write("أدخل بيت الشعر الخاص بك والموديل سيرد عليك.")

# Using chat_input for a chat-like input experience
prompt = st.chat_input("اختر موضوع المحاورة الشعرية وابدأ المحاورة")

if prompt:
    # Display user message as "الشاعر"
    st.write(f"📝 الشاعر: {prompt}")

    # Generate response when the user provides input
    response = get_watsonx_response(prompt)

    # Display AI response as "الروبوت"
    st.write(f"🤖 الروبوت: {response}")
