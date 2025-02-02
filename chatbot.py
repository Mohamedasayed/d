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

# Conversation history (in-memory, for demo purposes)
conversation_history = []

# Function to generate the custom prompt
def get_prompt(user_input):
    return f"""
        if he ask in english:
        You are an expert travel guide and museum information assistant. 
        Answer user questions briefly and exclusively related to tourism, travel destinations, cultural sites, museums, 
        historical landmarks, art exhibitions, and travel tips. Provide detailed information on popular tourist spots, 
        museum exhibits, local history, cultural facts, and recommendations for travelers.

        else if he ask in arabic:
        أنت مرشد سياحي خبير ومساعد معلومات المتاحف. أجب على أسئلة المستخدم بإيجاز تتعلق حصريًا بالسياحة، وجهات السفر، المواقع الثقافية، المتاحف، المعالم التاريخية، المعارض الفنية، ونصائح السفر.

        Question: {user_input}
    """

# Function to generate the AI response
def generate_response(user_input):
    prompt = get_prompt(user_input)
    response = genai.generate_text(prompt=prompt)
    return response.get('content', 'Sorry, I could not generate a response.')

# Endpoint to receive the user prompt
@app.route('/api/prompt', methods=['POST'])
def receive_prompt():
    data = request.json
    user_input = data.get("user_input")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # Generate AI response                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    try:
        response_text = generate_response(user_input)
        # Add to conversation history
        conversation_history.append({"user": user_input, "bot": response_text})
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to fetch conversation history
@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(conversation_history)

# Flask app export for Vercel
if __name__ == "__main__":
    app.run(debug=True)