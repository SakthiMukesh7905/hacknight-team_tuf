from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/')
def show_progress():
    return render_template("progress.html")

@app.route('/api/progress')
def progress():
    conn = sqlite3.connect('fitness_tracker.db')
    cursor = conn.cursor()

    # Get total calories grouped by food name
    cursor.execute("SELECT food, SUM(calories) FROM food_logs GROUP BY food")
    food_data = cursor.fetchall()
    food_names = [row[0] for row in food_data]
    food_calories = [row[1] for row in food_data]

    # Get total calories burned grouped by exercise name
    cursor.execute("SELECT exercise, SUM(burned_calories) FROM exercise_logs GROUP BY exercise")
    exercise_data = cursor.fetchall()
    exercise_names = [row[0] for row in exercise_data]
    exercise_calories = [row[1] for row in exercise_data]

    conn.close()

    return jsonify({
        'food_names': food_names,
        'food_calories': food_calories,
        'exercise_names': exercise_names,
        'exercise_calories': exercise_calories
    })

if __name__ == '__main__':
    app.run(port = 5003,debug=True)
