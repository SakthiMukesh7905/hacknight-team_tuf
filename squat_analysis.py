import cv2
import mediapipe as mp
import numpy as np

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Global variables for rep counter
rep_count = 0
rep_active = False
counter_enabled = False  # Toggle for rep counter

def toggle_counter():
    """Toggle the squat rep counter and reset when enabled."""
    global rep_count, counter_enabled
    counter_enabled = not counter_enabled
    if counter_enabled:
        rep_count = 0  # Reset counter when enabled

def calculate_angle(a, b, c):
    """Calculate the angle between three points."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def process_video(video_source):
    global rep_count
    cap = cv2.VideoCapture(video_source)
    holistic = mp_holistic.Holistic(min_detection_confidence=0.75, min_tracking_confidence=0.75)
    rep_count = 0

    base_width = 640  # Reference width for font scaling
    font_scale_ratio = 0.8  # Adjust this to fine-tune text size

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        height, width, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)
        
        feedback = "No Pose Detected"

        if results.pose_landmarks:
            feedback = analyze_frame(results.pose_landmarks.landmark, width, height)

            # Draw landmarks
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            
            # Dynamic font scaling
            font_scale = (width / base_width) * font_scale_ratio

            # Add feedback text with dynamically adjusted font size
            cv2.putText(frame, feedback, (int(20 * (width / base_width)), int(50 * (height / base_width))),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), int(3 * font_scale))

            # Display Rep Count if enabled
            cv2.putText(frame, f"Reps: {rep_count}", (int(20 * (width / base_width)), int(120 * (height / base_width))),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), int(3 * font_scale))

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    cap.release()
    cv2.destroyAllWindows()

def analyze_frame(landmarks, width, height):
    """Analyze squat form and count reps."""
    global rep_count, rep_active

    hip = [int(landmarks[mp_holistic.PoseLandmark.LEFT_HIP.value].x * width),
           int(landmarks[mp_holistic.PoseLandmark.LEFT_HIP.value].y * height)]
    knee = [int(landmarks[mp_holistic.PoseLandmark.LEFT_KNEE.value].x * width),
            int(landmarks[mp_holistic.PoseLandmark.LEFT_KNEE.value].y * height)]
    ankle = [int(landmarks[mp_holistic.PoseLandmark.LEFT_ANKLE.value].x * width),
             int(landmarks[mp_holistic.PoseLandmark.LEFT_ANKLE.value].y * height)]
    shoulder = [int(landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].x * width),
                int(landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].y * height)]
    
    knee_angle = calculate_angle(hip, knee, ankle)
    back_angle = calculate_angle(shoulder, hip, knee)

    feedback = "Good squat!"

    # Squat-specific feedback conditions
    if back_angle < 45:
        feedback = "Straighten your back!"
    elif knee_angle > 160:
        feedback = "Lower deeper!"
    elif knee_angle < 100:
        feedback = "Descend further!"
    elif abs(knee[0] - ankle[0]) > 50:
        feedback = "Keep knees behind toes!"

    # Rep Counter Logic
    if knee_angle < 100 and not rep_active:  # Bottom position of squat
        rep_active = True  
    elif knee_angle > 160 and rep_active:  # Standing up (rep completed)
        rep_count += 1  
        rep_active = False  # Reset for next rep

    return feedback

def process_squat_video(video_source):
    return process_video(video_source)
