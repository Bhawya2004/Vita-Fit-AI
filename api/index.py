from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import base64
import json

# Change the app initialization to include template and static folders
app = Flask(__name__, 
    static_folder='../static',
    template_folder='../templates'
)
CORS(app)

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found. Please set it in a .env file.")
    exit(1)

# Initialize chat sessions storage
chat_sessions = {}

ROLE_INSTRUCTION = """
You are an AI gym trainer named FitBot developed by Bhawya. You specialize in fitness-related topics and can provide advice on workouts, exercises, diet plans, injury prevention, and proper form. Your goal is to provide concise, helpful, and friendly responses to users' fitness inquiries.
You should:
- Keep responses minimal and to the point.
- Stay within the domain of fitness and exercise advice.
- Never provide information unrelated to fitness topics.
- Redirect users if they ask about non-fitness subjects.
- End responses on a positive note.
"""

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        image_data = data.get('image', None)
        
        if not user_message and not image_data:
            return jsonify({'error': 'No message or image provided'}), 400
            
        response = chat_with_gemini(user_message, session_id, image_data)
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def chat_with_gemini(prompt, session_id, image_data=None):
    try:
        # Initialize or get existing chat history
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        # Get current session history
        session_history = chat_sessions[session_id]
        
        # Build context from history
        context = ROLE_INSTRUCTION + "\n\nPrevious conversation:\n"
        # Include entire conversation history instead of just last 3 messages
        for msg in session_history:
            context += f"{msg}\n"
        
        # Add current prompt
        user_prompt = f"User: {prompt}"
        if image_data:
            user_prompt += " (image attached)"
        
        # For history tracking
        session_history.append(user_prompt)
        
        # API endpoint
        api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={api_key}"
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # For multimodal input handling
        if image_data:
            # Remove data URL prefix if present
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]
            
            # Prepare request payload with image
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": context + "\n" + user_prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_data
                                }
                            }
                        ]
                    }
                ]
            }
        else:
            # Text-only payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": context + "\n" + user_prompt}
                        ]
                    }
                ]
            }
        
        # Make API request
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Process response
        if response.status_code == 200:
            response_json = response.json()
            
            # Extract text from response
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                candidate = response_json["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        response_text = parts[0]["text"].strip()
                        
                        # Store the conversation
                        session_history.append(f"Assistant: {response_text}")
                        
                        return response_text
        
        # If we get here, something went wrong
        print(f"API response: {response.status_code}, {response.text}")
        return "I'm having trouble understanding. Could you rephrase that?"

    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return "I'm having trouble connecting. Please try again."

@app.route('/clear-history', methods=['POST'])
def clear_history():
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in chat_sessions:
            chat_sessions[session_id] = []
            
        return jsonify({'message': 'Chat history cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-history', methods=['GET'])
def get_history():
    try:
        session_id = request.args.get('session_id', 'default')
        history = chat_sessions.get(session_id, [])
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a route for the root URL
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    print(f"Starting server with API key: {api_key[:10]}...")
    app.run(debug=True, port=5000)