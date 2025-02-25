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

# Add fitness data directly in this file
FITNESS_RESPONSES = {
    "yoga": {
        "definition": "Yoga is an ancient practice that combines physical postures (asanas), breathing techniques (pranayama), meditation, and philosophical principles. It promotes physical strength, flexibility, mental clarity, and emotional well-being.",
        "benefits": [
            "Improves flexibility and balance",
            "Reduces stress and anxiety",
            "Builds strength and endurance",
            "Enhances mindfulness",
            "Improves breathing",
            "Helps with pain management"
        ],
        "types": [
            "Hatha Yoga - Gentle, basic yoga",
            "Vinyasa - Flow-based yoga",
            "Ashtanga - More intense, structured yoga",
            "Yin Yoga - Slow-paced, holding poses",
            "Kundalini - Spiritual and physical practice"
        ]
    },
    "workout": {
        "types": [
            "Strength Training",
            "Cardio",
            "HIIT",
            "Flexibility",
            "Balance"
        ],
        "tips": [
            "Start slowly and progress gradually",
            "Maintain proper form",
            "Stay hydrated",
            "Get adequate rest",
            "Eat a balanced diet"
        ]
    },
    "nutrition": {
        "principles": [
            "Eat a variety of whole foods",
            "Balance macronutrients (protein, carbs, fats)",
            "Stay hydrated throughout the day",
            "Consume adequate protein for muscle recovery",
            "Time meals around workouts for optimal performance"
        ],
        "tips": [
            "Meal prep to maintain consistency",
            "Read nutrition labels carefully",
            "Focus on nutrient density, not just calories",
            "Adjust intake based on activity level",
            "Allow occasional treats for sustainability"
        ]
    },
    "appreciation_responses": [
        "You're welcome! 💪 I'm glad I could help. Is there anything else about fitness you'd like to know?",
        "My pleasure! 🌟 I'm here to support your fitness journey. What else can I help with?",
        "Happy to help! 😊 Let me know if you have more fitness questions!",
        "Anytime! 🏋️ Your fitness goals are important. What else would you like to discuss?",
        "Glad I could assist! 🍎 Remember, consistency is key to fitness success. Anything else you're curious about?"
    ],
    "cardio": {
        "definition": "Cardiovascular exercise is any activity that increases your heart rate and breathing, improving heart and lung fitness.",
        "types": [
            "Running - High impact, great calorie burner",
            "Swimming - Full body, low impact",
            "Cycling - Low impact, good for joints",
            "Jump Rope - High intensity, improves coordination",
            "Walking - Beginner friendly, low impact"
        ],
        "benefits": [
            "Improves heart health",
            "Burns calories effectively",
            "Increases stamina and endurance",
            "Reduces stress",
            "Helps with weight management"
        ]
    },
    "weight_training": {
        "definition": "Weight training involves using resistance to build strength, muscle mass, and endurance.",
        "principles": [
            "Progressive overload - Gradually increase weight/reps",
            "Proper form - Essential for results and safety",
            "Rest between sets - Allows muscle recovery",
            "Balanced routine - Work all major muscle groups",
            "Recovery days - Prevent overtraining"
        ],
        "exercises": [
            "Squats - Lower body compound movement",
            "Deadlifts - Full body strength builder",
            "Bench Press - Upper body push exercise",
            "Rows - Back and pulling strength",
            "Overhead Press - Shoulder development"
        ]
    },
    "stretching": {
        "types": [
            "Dynamic - Active movements before exercise",
            "Static - Hold positions after workout",
            "PNF - Contract-relax technique",
            "Ballistic - Bouncing movements (advanced)",
            "Active - Holding position using muscles"
        ],
        "benefits": [
            "Improves flexibility",
            "Reduces muscle tension",
            "Prevents injury",
            "Enhances recovery",
            "Increases range of motion"
        ],
        "tips": [
            "Warm up before stretching",
            "Don't bounce in static stretches",
            "Hold stretches for 15-30 seconds",
            "Breathe deeply and regularly",
            "Never stretch to pain"
        ]
    }
}

def get_fitness_response(query):
    """
    Process fitness-related queries and return appropriate responses
    """
    query = query.lower().strip()
    
    # Check for appreciation phrases
    appreciation_keywords = ["thanks", "thank you", "thx", "appreciate", "good", "great", "awesome", "excellent", "nice", "cool", "helpful"]
    if any(keyword in query for keyword in appreciation_keywords) and len(query.split()) < 5:
        import random
        return random.choice(FITNESS_RESPONSES["appreciation_responses"])
    
    if "yoga" in query:
        yoga_info = FITNESS_RESPONSES["yoga"]
        return f"""
Yoga: {yoga_info['definition']}

Key Benefits:
{chr(10).join('- ' + benefit for benefit in yoga_info['benefits'])}

Common Types:
{chr(10).join('- ' + type for type in yoga_info['types'])}
"""
    
    if "workout" in query:
        workout_info = FITNESS_RESPONSES["workout"]
        return f"""
Workout Types:
{chr(10).join('- ' + type for type in workout_info['types'])}

Important Tips:
{chr(10).join('- ' + tip for tip in workout_info['tips'])}
"""
    
    if "nutrition" in query or "diet" in query or "food" in query or "eat" in query:
        nutrition_info = FITNESS_RESPONSES["nutrition"]
        return f"""
Nutrition Principles:
{chr(10).join('- ' + principle for principle in nutrition_info['principles'])}

Practical Tips:
{chr(10).join('- ' + tip for tip in nutrition_info['tips'])}

Remember that nutrition needs vary based on individual goals, body type, and activity level. Consider consulting with a registered dietitian for personalized advice.
"""
    
    if "cardio" in query:
        cardio_info = FITNESS_RESPONSES["cardio"]
        return f"""
Cardio Exercise: {cardio_info['definition']}

Types of Cardio:
{chr(10).join('- ' + type for type in cardio_info['types'])}

Benefits:
{chr(10).join('- ' + benefit for benefit in cardio_info['benefits'])}
"""

    if "weight" in query or "strength" in query:
        weight_info = FITNESS_RESPONSES["weight_training"]
        return f"""
Weight Training: {weight_info['definition']}

Key Principles:
{chr(10).join('- ' + principle for principle in weight_info['principles'])}

Basic Exercises:
{chr(10).join('- ' + exercise for exercise in weight_info['exercises'])}
"""

    if "stretch" in query or "flexibility" in query:
        stretch_info = FITNESS_RESPONSES["stretching"]
        return f"""
Types of Stretching:
{chr(10).join('- ' + type for type in stretch_info['types'])}

Benefits:
{chr(10).join('- ' + benefit for benefit in stretch_info['benefits'])}

Important Tips:
{chr(10).join('- ' + tip for tip in stretch_info['tips'])}
"""
    
    return "I'm here to help with your fitness questions! Please ask about specific topics like yoga, workouts, nutrition, or exercise techniques."

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
        # Keep search terms in both languages for videos only
        query_languages = [
            f"how to {query} tutorial form technique",
            f"how to {query} guide exercise",
            f"best {query} tutorial",
            f"{query} tutorial hindi",  # Keep Hindi option for videos only
            f"कैसे करें {query} एक्सरसाइज"  # Keep Hindi option for videos only
        ]
        
        # Randomly select a search query
        import random
        search_query = random.choice(query_languages)
        
        # Request more results to choose from
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&type=video&key={youtube_api_key}&maxResults=5&relevanceLanguage=en,hi"
        response = requests.get(search_url)
        data = response.json()

        if 'items' in data and data['items']:
            # Randomly select one video from the results
            video = random.choice(data['items'])
            video_id = video['id']['videoId']
            video_title = video['snippet']['title']
            
            # Add language indicator to the title
            is_hindi = any(hindi_term in video_title.lower() for hindi_term in ['hindi', 'हिंदी'])
            language_indicator = "🇮🇳" if is_hindi else "🇬🇧"
            
            return {
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'title': f"{language_indicator} {video_title}"
            }
        return None
    except Exception as e:
        print(f"Error fetching YouTube link: {e}")
        return None

ROLE_INSTRUCTION = """
You are FitBot, an AI fitness trainer specializing in exercise, nutrition, and wellness. 
Always respond in English only.

For greetings (like "hi", "hello", "good morning", etc.), respond warmly with a greeting and invite them to ask about fitness:
- "Hello! 👋 I'm your personal fitness assistant. How can I help you with your fitness journey today?"
- "Hi there! 🌟 Ready to help you achieve your fitness goals. What would you like to know?"
- "Good morning/afternoon/evening! 💪 I'm here to assist with your fitness questions!"

For fitness queries, format your responses as follows:

Guide to [Exercise/Topic]

Steps:
• First step
• Second step
• Third step

Key Tips:
• Important tip 1
• Important tip 2

Additional Information:
[First paragraph with key information]

[Second paragraph with more details]

Safety Note:
[Important safety considerations]

For non-fitness queries, respond with:
"I'm your fitness assistant. I can help you with exercise, nutrition, and wellness questions. Please ask me something related to fitness!"

Remember to:
• Only provide fitness-related information
• Be encouraging and motivational
• Never provide medical advice
• Keep focus on fitness and wellness topics
• Politely redirect non-fitness queries
• Always respond in English only
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
        
        # Check for appreciation messages first
        appreciation_keywords = ["thanks", "thank you", "thx", "appreciate", "good", "great", "awesome", "excellent", "nice", "cool", "helpful"]
        if any(keyword in user_message for keyword in appreciation_keywords) and len(user_message.split()) < 5:
            import random
            response = random.choice(FITNESS_RESPONSES["appreciation_responses"])
        # Then check if it's a fitness-related query
        elif any(keyword in user_message for keyword in ["workout", "exercise", "fitness", "yoga", "gym", "diet", "nutrition", "cardio", "weight", "strength", "stretch", "flexibility"]):
            response = get_fitness_response(user_message)
        else:
            # If not fitness-related, use Gemini
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
            youtube_data = get_youtube_link(user_message)
            if youtube_data:
                response += f"\n\nFor visual guidance, you can watch this helpful video:\n{youtube_data['title']}\n{youtube_data['url']}\n\nNote: I provide different video suggestions each time to offer various teaching styles and perspectives."
        
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
        }],
        "generationConfig": {
            "stopSequences": ["हिंदी", "hindi"],  # Add stop sequences for non-English content
            "temperature": 0.7
        }
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