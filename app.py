from flask import Flask, render_template, request, Response, redirect, url_for, jsonify
import mysql.connector
import cv2
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL Database Connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Magic@2005',
    database='gym_ai'
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS workouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    workout_name VARCHAR(50),
    reps INT,
    duration INT
)''')
conn.commit()

# Video capture (For Live Camera)
video_capture = None

def generate_frames():
    global video_capture
    if video_capture is None:
        video_capture = cv2.VideoCapture(0)
    
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/deadlift')
def deadlift():
    return render_template('deadlift.html')

@app.route('/squat')
def squat():
    return render_template('squat.html')

@app.route('/pushup')
def pushup():
    return render_template('pushup.html')

@app.route('/live_deadlift')
def live_deadlift():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_live_deadlift', methods=['POST'])
def stop_live_deadlift():
    global video_capture
    if video_capture is not None:
        video_capture.release()
        video_capture = None
    return '', 204

@app.route('/upload_deadlift', methods=['POST'])
def upload_deadlift():
    if 'video' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(file_path)
    return jsonify({'video_path': file_path, 'feedback': 'Video uploaded successfully'})

@app.route('/store_workout', methods=['POST'])
def store_workout():
    data = request.json
    workout_name = data.get('workout_name')
    reps = data.get('reps')
    duration = data.get('duration')

    cursor.execute("INSERT INTO workouts (workout_name, reps, duration) VALUES (%s, %s, %s)", (workout_name, reps, duration))
    conn.commit()

    return jsonify({'message': 'Workout stored successfully'})

if __name__ == '__main__':
    app.run(debug=True)
