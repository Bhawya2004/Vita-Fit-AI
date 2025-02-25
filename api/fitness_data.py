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