import cv2
import mediapipe as mp
import numpy as np

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

rep_count = 0
rep_active = False
counter_enabled = False  # Toggle for rep counte



def toggle_counter():
    global rep_count, counter_enabled
    counter_enabled = not counter_enabled
    if counter_enabled:
        rep_count = 0  # Reset counter when enabled

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def process_video(video_source):
    global rep_count, rep_active, counter_enabled

    # Initialize counters at function start
    rep_count = 0
    rep_active = False
    counter_enabled = False

    cap = cv2.VideoCapture(video_source)
    holistic = mp_holistic.Holistic(min_detection_confidence=0.75, min_tracking_confidence=0.75)

    base_width = 640  # Reference width for standard font scaling
    font_scale_ratio = 0.8  # Adjust this to fine-tune the size

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

        # Calculate dynamic font scale
        font_scale = (width / base_width) * font_scale_ratio

        # Draw landmarks
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

        # Display feedback text with dynamic font size
        cv2.putText(frame, feedback, (int(20 * (width / base_width)), int(50 * (height / base_width))),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), int(3 * font_scale))

        cv2.putText(frame, f"Reps: {rep_count}", (int(20 * (width / base_width)), int(120 * (height / base_width))),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), int(3 * font_scale))

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()


def analyze_frame(landmarks, width, height):
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

    feedback = "Good deadlift!"

    if back_angle < 70:
        feedback = "Straighten your back!"
    elif knee_angle < 140:
        feedback = "Extend knees more!"
    elif hip[1] < shoulder[1]:
        feedback = "Hips too low!"

    # Rep Counter Logic
    if knee_angle < 100 and not rep_active:
            rep_active = True  # Bottom position
    elif knee_angle > 160 and rep_active:
            rep_count += 1  # Completed rep
            rep_active = False  # Reset for next rep

    return feedback

def process_deadlift_video(video_source):
    return process_video(video_source)
