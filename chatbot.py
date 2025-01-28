from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
google_api = os.getenv("GOOGLE_API_KEY")

# Configure the Google Generative AI client
if google_api:
    genai.configure(api_key=google_api)
else:
    raise EnvironmentError("Google API key is not found or incorrect.")

# Initialize Flask app
app = Flask(__name__)

# Conversation history to simulate state (can use a database for persistence in production)
conversation_history = []

# Function to generate the custom prompt with history
# def get_prompt(user_input):
#     conversation = "\n".join(
#         f"User: {entry['user']}\nBot: {entry['bot']}" for entry in conversation_history
#     )
#     return f"""
#         You are an expert travel guide and museum information assistant.
#         Answer user questions briefly and exclusively related to tourism, travel destinations, cultural sites, museums,
#         historical landmarks, art exhibitions, and travel tips. Provide detailed information on popular tourist spots,
#         museum exhibits, local history, cultural facts, and recommendations for travelers.

#         If the user asks questions outside of tourism or museums, politely redirect them back to relevant topics by saying,
#         'I’m here to assist you with questions about tourism, museums, and cultural sites.'

#         Conversation History:
#         {conversation}

#         Question: {user_input}
#     """


def get_prompt(user_input):
    # Build a history prompt from previous messages
    conversation = "\n".join(
        f"User: {entry['user']}\nBot: {entry['bot']}" for entry in st.session_state.conversation_history
    )
    # Add the current question to the conversation history
    return f"""
        if he ask in english:
        You are an expert travel guide and museum information assistant. 
        Answer user questions briefly and exclusively related to tourism, travel destinations, cultural sites, museums, 
        historical landmarks, art exhibitions, and travel tips. Provide detailed information on popular tourist spots, 
        museum exhibits, local history, cultural facts, and recommendations for travelers.
        
        If the user asks questions outside of tourism or museums, politely redirect them back to relevant topics 
        by saying, 'I’m here to assist you with questions about tourism, museums, and cultural sites.', also if he asking about anything related to ancient egyptian history pls reply briefly with details.

        else if he ask in arabic:
        أنت مرشد سياحي خبير ومساعد معلومات المتاحف. أجب على أسئلة المستخدم بإيجاز تتعلق حصريًا بالسياحة، وجهات السفر، المواقع الثقافية، المتاحف، المعالم التاريخية، المعارض الفنية، ونصائح السفر. قدم معلومات مفصلة عن الأماكن السياحية الشهيرة، المعروضات في المتاحف، التاريخ المحلي، الحقائق الثقافية، والتوصيات للمسافرين.

إذا طرح المستخدم أسئلة خارج نطاق السياحة أو المتاحف، قم بتحويله بلطف إلى المواضيع ذات الصلة بقولك: "أنا هنا لمساعدتك في أسئلة حول السياحة والمتاحف والمواقع الثقافية."، وإذا كان يسأل عن أي شيء يتعلق بتاريخ مصر القديمة، يرجى الرد بإيجاز مع تفاصيل.

        Conversation History:
        {conversation}

        Question: {user_input}
    """

# Function to generate the AI response


def generate_response(user_input):
    prompt = get_prompt(user_input)
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# Endpoint to receive the user prompt


@app.route('/api/prompt', methods=['POST'])
def receive_prompt():
    data = request.json
    user_input = data.get("user_input")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # Generate AI response
    response_text = generate_response(user_input)

    # Add to conversation history
    conversation_history.append({"user": user_input, "bot": response_text})

    return jsonify({"response": response_text})

# Endpoint to fetch conversation history


@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(conversation_history)

# Export the app for Vercel


def handler(event, context):
    from flask_lambda import FlaskLambda
    app_lambda = FlaskLambda(app)
    return app_lambda(event, context)
