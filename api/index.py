try:
    from flask import Flask, request, jsonify, render_template
    from flask_cors import CORS
except ImportError as e:
    print(f"Error importing Flask dependencies: {e}")
    print("Please install required packages using:")
    print("pip install flask flask-cors google-api-python-client")
    exit(1)
import requests 
import os
from dotenv import load_dotenv 

app = Flask(__name__, 
    static_folder='../static',
    template_folder='../templates'
)
CORS(app)

# Load API keys from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

# Remove debug prints for production
if not api_key or not youtube_api_key:
    print("Error: GEMINI_API_KEY or YOUTUBE_API_KEY not found. Please set them in .env file.")
    exit(1)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + api_key

def get_youtube_link(query):
    try:
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={youtube_api_key}&maxResults=1"
        response = requests.get(search_url)
        data = response.json()

        if 'items' in data:
            video_id = data['items'][0]['id']['videoId']
            video_title = data['items'][0]['snippet']['title']
            return {
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'title': video_title
            }
        return None
    except Exception as e:
        print(f"Error fetching YouTube link: {e}")
        return None

ROLE_INSTRUCTION = """
You are an AI fitness trainer named FitBot, specializing in exercise, nutrition, and wellness. Format your responses as follows:

Guide to [Exercise/Topic]\n\n

Steps:\n
• First step\n
• Second step\n
• Third step\n\n

Key Tips:\n
• Important tip 1\n
• Important tip 2\n\n

Additional Information:\n
[First paragraph with key information]\n\n

[Second paragraph with more details]\n\n

[Third paragraph if needed]\n\n

Safety Note:\n
[Important safety considerations]\n\n

Remember to:\n
• Create clear, descriptive headings\n
• Add double line breaks between sections\n
• Break down steps with bullet points\n
• Separate information into distinct paragraphs\n
• Include relevant safety warnings\n
• Be encouraging and motivational\n
• Never provide medical advice\n
• Keep focus on fitness and wellness topics
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip().lower()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
            
        # Get Gemini response first
        response = chat_with_gemini(user_message)
        
        # Expand exercise keywords list
        exercise_keywords = [
            'exercise', 'workout', 'fitness', 'training', 'posture', 
            'form', 'technique', 'routine', 'stretching', 'yoga',
            'gym', 'bodyweight', 'strength', 'cardio', 'warmup',
            'cooldown', 'deadlift', 'squat', 'pushup', 'plank',
            'burpee', 'lunge', 'crunch', 'pullup', 'bench press',
            'shoulder press', 'bicep', 'tricep', 'core', 'abs',
            'leg day', 'muscle', 'weight lifting', 'dumbbell',
            'kettlebell', 'resistance band', 'hiit', 'crossfit'
        ]
        
        # Check if query is exercise-related and contains form/technique questions
        needs_video = any(keyword in user_message for keyword in exercise_keywords) and any(term in user_message for term in ['how to', 'form', 'technique', 'guide', 'tutorial', 'demonstrate', 'show me', 'example'])
        
        if needs_video:
            youtube_data = get_youtube_link(f"how to {user_message} tutorial form technique")
            if youtube_data:
                response += f"\n\nFor visual guidance, you can watch this helpful video:\n{youtube_data['title']}\n{youtube_data['url']}"
        
        # Add typing effect flag to response
        return jsonify({
            'response': response,
            'shouldType': True  # New flag to indicate typing effect
        })
        
    except Exception as e:
        print(f"Error in chat route: {str(e)}")
        return jsonify({'error': str(e)}), 500

def chat_with_gemini(prompt):
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [{
            "role": "user",
            "parts": [{"text": ROLE_INSTRUCTION + "\nUser: " + prompt}]
        }]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        
        bot_response = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        if not bot_response:
            return "I'm here to assist with fitness inquiries. How can I help?"
        
        return bot_response.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error in Gemini API request: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later."
    except Exception as e:
        print(f"Unexpected error in chat_with_gemini: {str(e)}")
        return "I encountered an unexpected error. Please try again."

# Modified run configuration for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)