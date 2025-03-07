from flask import Flask, render_template
import sqlite3
import google.generativeai as genai
import os

# Initialize Flask App
app = Flask(__name__)

# Configure Gemini Pro
genai.configure(api_key="AIzaSyA-0rkCfbueku01YoBpVlktuxKZmqd7Z2U")

# Function to Get Exercise Logs from Database
def fetch_exercise_logs():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT exercise, duration, burned_calories FROM exercise_logs")
    exercise_logs = cursor.fetchall()
    conn.close()
    return exercise_logs

# Function to Get Food Suggestions from Gemini Pro
def get_food_suggestions(exercise_logs):
    if not exercise_logs:
        return ["No exercise data available to generate recommendations."]

    prompt = "Based on these exercises, suggest some healthy foods ranked with stars (⭐⭐⭐⭐⭐): Provide greater stars at first and lower stars at the last I need it in decending order. Include foods for up to 2 stars also..Provide 10 foods with their name and their rank alone with neatly formatted text, and do not provide any markdown astricks while generating the content.\n\n"
    for exercise, duration, burned_calories in exercise_logs:
        prompt += f"- {exercise}: {duration} mins, {burned_calories} kcal burned\n"

    prompt += "\nProvide a ranked food list in this format:\nOats ⭐⭐⭐⭐⭐\nBanana ⭐⭐⭐⭐\nChicken Breast ⭐⭐⭐⭐"

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    return response.text.split("\n") if response.text else ["No suggestions available."]

# Home Route
@app.route('/')
def index():
    # Fetch exercise logs from database
    exercise_logs = fetch_exercise_logs()
    
    # Generate food suggestions using Gemini Pro
    food_suggestions = get_food_suggestions(exercise_logs)

    return render_template("food.html",
                           exercise_logs=exercise_logs,
                           food_suggestions=food_suggestions)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
