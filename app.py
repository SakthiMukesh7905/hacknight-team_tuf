from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__, static_url_path='/static')  # Correct static path

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Sarath2733",
    database="fitness_db"
)
cursor = db.cursor()

# Predefined stretching exercise videos
stretching_videos = {
    "cardio": ["static/videos/cardio_stretch1.mp4",
               "static/videos/cardio_stretch2.mp4",
               "static/videos/cardio_stretch3.mp4",
               "static/videos/cardio_stretch4.mp4"
               ],
    "strength": ["static/videos/strength_stretch1.mp4",
                 "static/videos/strength_stretch2.mp4",
                 "static/videos/strength_stretch3.mp4",
                 "static/videos/strength_stretch5.mp4"
                 ],
    "yoga": [
        "static/videos/yoga_cooldown2.mp4",
        "static/videos/yoga_cooldown3.mp4",
        "static/videos/yoga_cooldown4.mp4",
        "static/videos/yoga_cooldown1.mp4"
    ],
    "general": ["static/videos/general_cooldown2.mp4"]
}

# Predefined Text-to-Speech (TTS) instructions
stretching_instructions = {
    "cardio": "Perform a full-body stretch, focusing on your legs and arms. Hold each stretch for 15-30 seconds.",
    "strength": "Focus on stretching your muscles after strength training. Hold each stretch for at least 30 seconds.",
    "yoga": "Cool down with deep breathing and slow stretches. Hold each position for 20-40 seconds.",
    "general": "Perform a light full-body stretch. Hold each stretch for 15-20 seconds."
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_recovery', methods=['POST'])
def get_recovery():
    data = request.json
    workout_type = data.get("workout_type", "general")
    
    # Fetch video suggestion and TTS instruction
    video_urls = stretching_videos.get(workout_type, stretching_videos["general"])
    tts_instruction = stretching_instructions.get(workout_type, stretching_instructions["general"])
    
    # Store user workout session in MySQL
    cursor.execute("INSERT INTO workout_history (workout_type, video_url) VALUES (%s, %s)", 
                   (workout_type, ", ".join(video_urls)))  # Store as a comma-separated string
    db.commit()
    
    return jsonify({"video_urls": video_urls, "tts_instruction": tts_instruction})

if __name__ == '__main__':
    app.run(debug=True)
