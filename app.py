from flask import Flask, render_template, request, jsonify
import os
from ibm_watsonx_ai.foundation_models import Model
from flask_cors import CORS
from functools import lru_cache
from threading import Thread
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to get credentials for IBM Watsonx
def get_credentials():
    return {
        "url": "https://eu-de.ml.cloud.ibm.com",
        "apikey": "PxrEtdAhNUfC4zNk7haVaFiF95fczhvNFj_ghIWGxDFu"
    }

# Caching the Watsonx model to avoid reloading on each request
@lru_cache(maxsize=1)
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

# Lazy loading Ashaar model only when needed
def baita():
    from Ashaar.bait_analysis import BaitAnalysis
    return BaitAnalysis()

@lru_cache(maxsize=1)
def get_analysis_model():
    return baita()

# Analyze poetry input using the cached analysis model
def analyze_poetry(analysis_model, baits):
    return analysis_model.analyze(baits, override_tashkeel=True)

# Arabic dictionary for number of verses
baits_dict = {
    1: "بيتا واحد",
    2: "بيتان اثنان",
    3: "ثلاثة أبيات",
    4: "أربعة أبيات",
    5: "خمسة أبيات",
    # يمكن إضافة المزيد حسب الحاجة
}

# Generate prompt for Watsonx model
def create_allam_prompt(user_input, analysis_result, baits_count):
    # Use the dictionary to get the Arabic equivalent of the verse count
    baits_count_arabic = baits_dict.get(baits_count, f"{baits_count} أبيات")  # Default if count is not in the dictionary
    print(baits_count_arabic)
    prompt_input = f"""<<SYS>>
    أنت شاعر متمرس في فن المحاورة الشعرية. عند تلقيك لأبيات شعرية من المستخدم، يجب عليك:
    1. الرد بنفس القافية المستخدمة في الأبيات المدخلة ({analysis_result['qafiyah']}) .
    2. الحفاظ على الوزن الشعري الخاص بالبحر المستخدم في الأبيات ({analysis_result['meter']}) .
    3. يجب أن يكون ردك يعكس نفس المعنى الموجودة في الأبيات الأساسية.
    4. يجب ان يكون ردك مكون من {baits_count_arabic} فقط. 
    <</SYS>>\n"""
    print(prompt_input)
    formatted_question = f"<s> [INST] {user_input} [/INST]"
    return f"{prompt_input}\n\n{formatted_question}"

# Background function to load models at startup
def load_models_in_background():
    print("Loading models in the background...")
    initialize_model()
    get_analysis_model()
    print("Models loaded successfully.")

# Route to serve the index.html file
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle the chat request
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('message')
    if not question:
        return jsonify({'error': 'No message provided'}), 400

    # Split and count baits (verses)
    baits = question.split("\n")
    baits_count = len(baits)
    print("baits", baits_count)

    # Get cached models
    analysis_model = get_analysis_model()
    watsonx_model = initialize_model()

    # Analyze the baits
    analysis_result = analyze_poetry(analysis_model, baits)
    print("analysis_result", analysis_result)

    # Create Watsonx prompt
    allam_prompt = create_allam_prompt(question, analysis_result, baits_count)

    # Generate response from Watsonx model
    generated_response = watsonx_model.generate_text(prompt=allam_prompt, guardrails=False)

    return jsonify({'response': generated_response})

if __name__ == "__main__":
    # Start background thread to load models when the app starts
    Thread(target=load_models_in_background).start()
    app.run(debug=False)
