import pandas as pd
import os
import requests
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
from flask_cors import CORS
#from fitness_data import FITNESS_RESPONSES

# Define the base directory dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create data directory path
DATA_DIR = os.path.join(BASE_DIR, "data")

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Load datasets with proper error handling
def load_dataset(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            print(f"✅ Loaded {file_name} ({len(df)} rows)")
            return df
        else:
            print(f"⚠️ Warning: {file_name} not found. Initializing empty DataFrame.")
            return pd.DataFrame()  # Return an empty DataFrame if file is missing
    except Exception as e:
        print(f"❌ Error loading {file_name}: {e}")
        return pd.DataFrame()

# Load all datasets
smoothie_recipes = load_dataset("Smoothie-Recipes - Sheet1.csv")
nutrition_products = load_dataset("bodybuilding_nutrition_products.csv")
gym_dataset = load_dataset("megaGymDataset.csv")
final_dataset = load_dataset("final_dataset.csv")
exercise_dataset = load_dataset("exercise_dataset.csv")

# Function to calculate BMI and provide fitness recommendations
def calculate_bmi(weight, height):
    """Calculate BMI and return the category and recommendations."""
    bmi = weight / (height / 100) ** 2  # Convert height from cm to meters
    if bmi < 18.5:
        category = "Underweight"
        recommendation = "Consider a diet plan focused on weight gain."
    elif 18.5 <= bmi < 24.9:
        category = "Normal weight"
        recommendation = "Maintain your current diet and exercise routine."
    elif 25 <= bmi < 29.9:
        category = "Overweight"
        recommendation = "Consider a balanced diet and regular exercise."
    else:
        category = "Obese"
        recommendation = "Consult a healthcare provider for personalized advice."

    return bmi, category, recommendation

# Function to fetch exercise/machine details from dataset
def get_exercise_info(query):
    if exercise_dataset.empty:
        return None
    
    # Check for exercises
    exercise_info = exercise_dataset[exercise_dataset["Exercise"].str.contains(query, case=False, na=False)]
    if not exercise_info.empty:
        return exercise_info.iloc[0].to_dict()
    
    # Check for machines in gym dataset
    machine_info = gym_dataset[gym_dataset["Machine"].str.contains(query, case=False, na=False)]
    if not machine_info.empty:
        return machine_info.iloc[0].to_dict()
    
    return None

# Function to enhance dataset response using Gemini API
def enhance_with_gemini(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024
        }
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Data unavailable")
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
    
    return "Error fetching enhanced response."

# Modify existing fitness response function to use datasets

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
    # Add more categories like:
    # "nutrition"
    # "cardio"
    # "weight_training"
    # "stretching"
    # etc.
}

def get_fitness_response(query):
    """
    Process fitness-related queries and return appropriate responses
    """
    query = query.lower().strip()
    
    if "yoga" in query:
        yoga_info = FITNESS_RESPONSES["yoga"]
        return f"""
Yoga: {yoga_info['definition']}

Key Benefits:
{chr(10).join('- ' + benefit for benefit in yoga_info['benefits'])}

Common Types:
{chr(10).join('- ' + type for type in yoga_info['types'])}
"""
    
    # Add more query handlers here
    
    return "I'm here to help with your fitness questions! Please ask about specific topics like yoga, workouts, nutrition, or exercise techniques." 
def get_fitness_response(query):
    query = query.lower().strip()

    print(f"Received query: {query}")  # Debugging line

    # Check for diet plan requests
    if "diet plan" in query or "what should I eat" in query or "lose weight" in query:
        return """
Diet Plan for Weight Loss:

Caloric Intake:
• Aim for a caloric deficit of 300-500 calories below your maintenance level.
• Track your weight weekly to adjust caloric intake as needed.

Macronutrient Breakdown:
• Protein: 1.2-2.0g per kg of body weight to preserve muscle mass.
• Carbohydrates: 40-50% of total calories, focusing on whole grains and vegetables.
• Fats: 20-30% of total calories, prioritizing healthy fats.

Sample Meal Ideas:
1. Breakfast: Scrambled eggs with spinach and tomatoes.
2. Lunch: Grilled chicken salad with mixed greens and vinaigrette.
3. Snack: Carrot sticks with hummus.
4. Dinner: Baked salmon with quinoa and steamed broccoli.
5. Post-Workout: Protein shake with a banana.

Make sure to stay hydrated and include plenty of fruits and vegetables in your diet!
"""

    # Check for workout plan requests
    if "workout plan" in query or "workout" in query:
        return """
Here are two popular workout plans you can choose from:
1. **Push-Pull-Legs (PPL) Split**: 
   - Push Day: Chest, Shoulders, Triceps
   - Pull Day: Back, Biceps
   - Legs Day: Quadriceps, Hamstrings, Calves

2. **Bro Split**: 
   - Monday: Chest
   - Tuesday: Back
   - Wednesday: Shoulders
   - Thursday: Arms
   - Friday: Legs

Please specify which one you would like to know more about!
"""

    # Check for BMI calculation requests
    if "bmi" in query or "calculate my bmi" in query:
        return "Please provide your height in centimeters and weight in kilograms."

    # Capture height and weight input
    if "height" in query and "weight" in query:
        # Extract height and weight from the query
        height = 180  # Replace with actual extraction logic
        weight = 55    # Replace with actual extraction logic
        bmi, category, recommendation = calculate_bmi(weight, height)
        return f"Your BMI is {bmi:.2f}, which falls into the category: {category}. {recommendation}"

    # Check for chest exercise queries
    if "chest" in query:
        return """
Best Exercises for Chest:
1. Bench Press
2. Dumbbell Flyes
3. Push-Ups
4. Chest Press Machine
5. Incline Dumbbell Press

Make sure to maintain proper form and gradually increase weights!
"""

    # Check for cardio machine queries
    if "cardio" in query or "machine" in query:
        return """
Best Machines for Cardio:
1. Treadmill - Great for running and walking
2. Elliptical - Low-impact full-body workout
3. Stationary Bike - Good for leg strength and endurance
4. Rowing Machine - Full-body cardio workout
5. Stair Climber - Excellent for lower body strength

These machines can help improve cardiovascular fitness effectively!
"""

    # Check for specific exercise technique queries
    if "how to" in query or "technique" in query:
        if "squat" in query:
            return get_exercise_technique('squat')
        elif "bench press" in query:
            return get_exercise_technique('bench press')
        # Add more exercises as needed

    # General fallback response
    return f"""
I can help you with specific information about:

1. Exercise Techniques & Form
2. Machine & Equipment Usage
3. Workout Plans (PPL or Bro Split)
4. Nutrition & Diet Plans
5. Cardio & Stretching
6. Muscle-specific Training

Please ask a more specific question about any of these topics, and I'll provide detailed guidance!
"""

def get_exercise_technique(exercise):
    """Helper function for exercise techniques"""
    techniques = {
        'squat': """
How to Perform a Proper Squat:

Setup:
• Feet shoulder-width apart
• Toes slightly pointed out
• Core engaged

Movement:
1. Bend knees and hips simultaneously
2. Lower until thighs are parallel to ground
3. Keep chest up, back straight
4. Push through heels to stand

Common Mistakes:
• Knees caving in
• Heels lifting off ground
• Rounding lower back

Tips:
• Start with bodyweight
• Practice with light weights
• Focus on form over weight
""",
        # Add more exercises...
    }
    return techniques.get(exercise, "Please ask about a specific exercise technique.")

# Add helper functions for other response types...
def get_bulking_diet_plan():
    return """
Bulking Diet Plan:

Caloric Intake:
• Maintenance calories + 300-500 calories
• Track weight gain (0.5-1 lb per week)

Macronutrients:
• Protein: 1.6-2.2g per kg bodyweight
• Carbs: 45-60% of total calories
• Fats: 20-30% of total calories

Key Foods:
1. Protein Sources:
   • Chicken, beef, fish
   • Eggs, dairy
   • Protein shakes

2. Complex Carbs:
   • Rice, potatoes
   • Whole grain pasta
   • Oatmeal

3. Healthy Fats:
   • Nuts, avocados
   • Olive oil
   • Fish oil

Meal Timing:
• 4-6 meals per day
• Post-workout nutrition crucial
"""

def get_free_weight_alternatives(muscle):
    """Helper function for free weight alternatives by muscle group"""
    alternatives = {
        'chest': """
• Barbell Bench Press
• Dumbbell Press
• Push-Ups
• Dumbbell Flyes""",
        'back': """
• Barbell Rows
• Pull-Ups
• Dumbbell Rows
• Face Pulls""",
        'legs': """
• Barbell Squats
• Romanian Deadlifts
• Walking Lunges
• Bulgarian Split Squats""",
        'shoulders': """
• Military Press
• Dumbbell Shoulder Press
• Lateral Raises
• Front Raises""",
        'arms': """
• Barbell Curls
• Dumbbell Curls
• Diamond Push-Ups
• Close-Grip Bench Press"""
    }
    return alternatives.get(muscle, "• Basic free weight exercises recommended")

def get_yoga_info():
    """Helper function for yoga information"""
    yoga_info = FITNESS_RESPONSES["yoga"]
    return f"""
Yoga: {yoga_info['definition']}

Key Benefits:
{chr(10).join('• ' + benefit for benefit in yoga_info['benefits'])}

Common Types:
{chr(10).join('• ' + type for type in yoga_info['types'])}
"""

def get_cardio_info():
    """Helper function for cardio information"""
    cardio_info = FITNESS_RESPONSES["cardio"]
    return f"""
Cardio Exercise: {cardio_info['definition']}

Types of Cardio:
{chr(10).join('• ' + type for type in cardio_info['types'])}

Benefits:
{chr(10).join('• ' + benefit for benefit in cardio_info['benefits'])}
"""

def get_weight_training_info():
    """Helper function for weight training information"""
    weight_info = FITNESS_RESPONSES["weight_training"]
    return f"""
Weight Training: {weight_info['definition']}

Key Principles:
{chr(10).join('• ' + principle for principle in weight_info['principles'])}

Basic Exercises:
{chr(10).join('• ' + exercise for exercise in weight_info['exercises'])}
"""

def get_stretching_info():
    """Helper function for stretching information"""
    stretch_info = FITNESS_RESPONSES["stretching"]
    return f"""
Types of Stretching:
{chr(10).join('• ' + type for type in stretch_info['types'])}

Benefits:
{chr(10).join('• ' + benefit for benefit in stretch_info['benefits'])}

Important Tips:
{chr(10).join('• ' + tip for tip in stretch_info['tips'])}
"""

def get_general_nutrition_advice():
    """Helper function for general nutrition advice"""
    nutrition_info = FITNESS_RESPONSES["nutrition"]
    return f"""
Nutrition Principles:
{chr(10).join('• ' + principle for principle in nutrition_info['principles'])}

Practical Tips:
{chr(10).join('• ' + tip for tip in nutrition_info['tips'])}

Remember: Individual nutrition needs vary based on goals, body type, and activity level.
"""

def get_cutting_diet_plan():
    """Helper function for cutting diet plan"""
    return """
Cutting Diet Plan:

Caloric Intake:
• Maintenance calories - 300-500 calories
• Track weight loss (0.5-1 lb per week)

Macronutrients:
• Protein: 2.0-2.4g per kg bodyweight
• Carbs: 30-45% of total calories
• Fats: 20-25% of total calories

Key Foods:
1. Lean Protein Sources:
   • Chicken breast
   • Fish (tuna, salmon)
   • Egg whites
   • Low-fat dairy

2. Complex Carbs:
   • Vegetables
   • Brown rice
   • Sweet potatoes
   • Quinoa

3. Healthy Fats:
   • Avocados
   • Nuts (in moderation)
   • Olive oil
   • Fish oil

Meal Timing:
• 4-5 meals per day
• Pre and post-workout nutrition
• Higher carbs around workouts
"""

def format_exercise_response(exercise):
    """Helper function to format exercise dataset responses"""
    try:
        return f"""
Exercise: {exercise['Exercise']}

Target Muscle: {exercise.get('Target Muscle', 'Not specified')}
Equipment Needed: {exercise.get('Equipment', 'Not specified')}

Instructions:
{exercise.get('Instructions', 'Please consult a fitness professional for proper form')}

Tips:
• Focus on proper form
• Start with lighter weights
• Increase weight gradually
• Maintain controlled movement
"""
    except Exception as e:
        print(f"Error formatting exercise response: {e}")
        return "Error retrieving exercise information. Please try another exercise."

app = Flask(__name__, 
    static_folder='../static',
    template_folder='../templates'
)

CORS(app)

# Load and validate API keys
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

if not api_key or not youtube_api_key:
    print("Error: API keys not found in environment variables")
    print("Please check your .env file and Render environment settings")
    exit(1)

# Remove the API key format validation since it might vary
# if not api_key.startswith("AI") or len(api_key) < 20:
#     print("Error: Invalid Gemini API key format")
#     exit(1)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key=" + api_key

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
Your role is to be a highly knowledgeable fitness assistant. You must answer every fitness-related query, including:  

1️⃣ GENERAL FITNESS QUERIES:
When asked about basic concepts like "What is fitness?" or "What is a gym?", provide:
• Clear definition
• Main benefits
• Getting started tips
• Safety considerations

2️⃣ WORKOUT PLANS & EXERCISE GUIDANCE:
For workout plan requests:
FIRST ASK: "Would you prefer a Push-Pull-Legs (PPL) split or a Bro Split? 

• PPL Split: Trains each movement pattern twice per week
• Bro Split: Focuses on one muscle group per day

Then provide based on choice:
• Day-by-day breakdown
• Exercise selection
• Sets and reps
• Rest periods
• Progressive overload tips

For exercise technique queries:
[Exercise Name]

Step-by-Step Guide:
• Starting position
• Movement execution
• Breathing pattern
• Form cues

Common Mistakes:
• What to avoid
• Safety issues
• Corrections

3️⃣ DIET & NUTRITION ADVICE:
For diet plan requests:
FIRST ASK: "Are you trying to gain weight or lose weight?"

Then provide based on their answer:
[Goal-Specific Diet Plan]
• Daily caloric target
• Macronutrient breakdown
• Meal timing strategy
• Food options list
• Sample meal plan
• Supplement recommendations

4️⃣ MACHINE & EQUIPMENT GUIDANCE:
For equipment queries:
[Target Muscle/Exercise]

Machine Options:
• Best machines
• Proper setup
• Usage instructions
• Safety tips

Free Weight Alternatives:
• Exercise options
• Form guide
• Equipment needs

5️⃣ BMI CALCULATION & ANALYSIS:
When height and weight provided:
• Calculate BMI
• Classify as: Underweight/Normal/Overweight/Obese
• Provide relevant fitness recommendations
• Suggest appropriate workout adjustments
• Give specific nutrition advice

RESPONSE RULES:
1. Always provide clear, structured fitness information
2. Never reject valid fitness queries
3. Include safety guidelines
4. Suggest modifications for different levels
5. Base advice on scientific evidence

For non-fitness queries, respond:
"I specialize in fitness-related topics like workouts, nutrition, and exercise guidance. Let me know how I can help with your fitness journey!"

For greetings, respond:
"Hello! 👋 I'm your expert fitness advisor. I can help you with:
• Workout plans (PPL or Bro Split)
• Exercise techniques
• Nutrition guidance
• Equipment recommendations
• BMI analysis and advice

What would you like to know about? I'll provide detailed guidance based on your needs.

---

You are a knowledgeable and interactive fitness chatbot. Your goal is to assist users with **any fitness-related question**, including workouts, diet, gym exercises, BMI calculations, supplements, recovery, and general health.

🟢 **1️⃣ Answer All Fitness Questions**  
- Do **not** reject general fitness-related queries.  
- If a user asks *"What is fitness?"*, provide a definition.  
- If a user asks about gym equipment, suggest exercises that match their needs.  

🟢 **2️⃣ Be Flexible with Workouts & Diets**  
- If a user asks for a **workout plan**, provide **multiple options** instead of forcing only "Push-Pull-Legs" or "Bro Split."  
- If a user asks for a **diet plan**, do **not** ask only "gain weight or lose weight"—instead, allow flexible meal plan recommendations for different fitness goals.  

🟢 **3️⃣ Improve Machine & Exercise Recommendations**  
- If a user asks **"Which machine should I use for chest exercises?"**, suggest multiple machines and free-weight alternatives.  
- If a user asks **"Best exercises for legs?"**, provide compound and isolation exercises with variations.  

🟢 **4️⃣ Allow Broader Health & Recovery Topics**  
- If a user asks about **recovery strategies**, provide rest day recommendations, stretching, mobility drills, and active recovery tips.  
- If a user asks about **injury prevention**, suggest ways to avoid injuries and modify workouts accordingly.  

🟢 **5️⃣ Reduce Unnecessary Restrictions**  
- Do **not** reject fitness-related questions with a generic response like *"Please ask about workouts, nutrition, etc."*  
- Instead, **always attempt to provide a useful answer** using dataset information or external knowledge.  

🔴 **6️⃣ Limit Only Completely Unrelated Topics**  
- If the user asks about politics, programming, or unrelated topics, **redirect to fitness-related topics in a friendly manner.**  
  - Example: *"I specialize in fitness! However, I can help you find exercises that fit your lifestyle."*
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
        
        # First try fitness-specific responses
        fitness_keywords = ["workout", "exercise", "fitness", "yoga", "gym", "diet", "nutrition", "cardio", "weight", "strength", "stretch", "flexibility"]
        appreciation_keywords = ["thanks", "thank you", "thx", "appreciate", "good", "great", "awesome", "excellent", "nice", "cool", "helpful"]
        
        if any(keyword in user_message for keyword in appreciation_keywords) and len(user_message.split()) < 5:
            import random
            response = random.choice(FITNESS_RESPONSES["appreciation_responses"])
        elif any(keyword in user_message for keyword in fitness_keywords):
            response = get_fitness_response(user_message)
        else:
            # Only use Gemini for non-fitness queries
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

    # Enhanced list of non-fitness keywords
    non_fitness_keywords = [
        'medical', 'disease', 'diagnosis', 'therapy', 'depression', 'anxiety',
        'technology', 'computer', 'phone', 'politics', 'election', 'government',
        'finance', 'money', 'investment', 'relationship', 'breakup', 'dating',
        'programming', 'coding', 'software', 'hardware', 'crypto', 'stock market'
    ]

    # Check if the prompt contains non-fitness keywords
    if any(keyword in prompt.lower() for keyword in non_fitness_keywords):
        return 'I specialize in fitness-related topics like workouts, nutrition, and gym equipment. Let me know how I can help with your fitness journey!'

    data = {
        "contents": [{
            "role": "user",
            "parts": [{"text": ROLE_INSTRUCTION + "\nUser: " + prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        
        bot_response = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        if not bot_response:
            return """Hello! 👋 I'm your interactive fitness expert. I can help you with:

• Customized workout plans (PPL or Bro Split)
• Detailed exercise techniques
• Goal-specific diet plans
• Gym equipment guidance
• Supplement advice
• Recovery strategies

To provide the best guidance, I'll ask you some questions about your preferences. What would you like to know about?"""
        
        return bot_response.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error in Gemini API request: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later."
    except Exception as e:
        print(f"Unexpected error in chat_with_gemini: {str(e)}")
        return "I encountered an unexpected error. Please try again."

def list_available_models():
    try:
        # Add API key as query parameter
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print("\nAvailable Models:")
            for model in models.get('models', []):
                print(f"- Name: {model.get('name')}")
                print(f"  Display Name: {model.get('displayName')}")
                print(f"  Description: {model.get('description')}")
                print()
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error listing models: {str(e)}")

@app.route("/test-datasets")
def test_datasets():
    dataset_paths = [
        "data/000Smoothie-Recipes - Sheet1.csv",
        "data/bodybuilding_nutrition_products.csv",
        "data/megaGymDataset.csv",
        "data/final_dataset.csv",
        "data/exercise_dataset.csv"
    ]
    
    results = {}
    
    for path in dataset_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                results[path] = f"✅ Loaded {len(df)} rows."
            except Exception as e:
                results[path] = f"❌ Error loading: {e}"
        else:
            results[path] = "❌ File not found."
    
    return jsonify(results)

@app.route('/list-models', methods=['GET'])
def list_models_endpoint():
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': response.text}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Modified run configuration for Render
if __name__ == "__main__":
    # List models before starting the server
    # print("Checking available models...")
    # list_available_models()
    
    # Your existing code
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)