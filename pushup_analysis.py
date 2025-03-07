import cv2
import mediapipe as mp
import numpy as np

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def process_video(video_source):
    rep_count = 0  
    rep_status = "Up"  

    cap = cv2.VideoCapture(video_source)
    holistic = mp_holistic.Holistic(min_detection_confidence=0.75, min_tracking_confidence=0.75)

    base_width = 640  # Reference width for font scaling
    font_scale_ratio = 0.8  

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        height, width, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)

        if results.pose_landmarks:
            feedback, rep_count, rep_status = analyze_pushup(results.pose_landmarks.landmark, width, height, rep_count, rep_status)

            # Draw landmarks
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

            # Dynamic font scaling
            font_scale = (width / base_width) * font_scale_ratio

            # Display feedback text
            cv2.putText(frame, feedback, (int(20 * (width / base_width)), int(50 * (height / base_width))),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), int(2 * font_scale))

            # Display rep count
            cv2.putText(frame, f"Reps: {rep_count}", (int(20 * (width / base_width)), int(100 * (height / base_width))),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), int(2 * font_scale))

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()

def analyze_pushup(landmarks, width, height, rep_count, rep_status):
    shoulder = np.array([landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].x * width,
                         landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].y * height])
    elbow = np.array([landmarks[mp_holistic.PoseLandmark.LEFT_ELBOW.value].x * width,
                      landmarks[mp_holistic.PoseLandmark.LEFT_ELBOW.value].y * height])
    wrist = np.array([landmarks[mp_holistic.PoseLandmark.LEFT_WRIST.value].x * width,
                      landmarks[mp_holistic.PoseLandmark.LEFT_WRIST.value].y * height])
    hip = np.array([landmarks[mp_holistic.PoseLandmark.LEFT_HIP.value].x * width,
                    landmarks[mp_holistic.PoseLandmark.LEFT_HIP.value].y * height])
    knee = np.array([landmarks[mp_holistic.PoseLandmark.LEFT_KNEE.value].x * width,
                     landmarks[mp_holistic.PoseLandmark.LEFT_KNEE.value].y * height])

    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    spine_angle = calculate_angle(shoulder, hip, knee)

    feedback = []

    if hip[1] < shoulder[1] - 20:  
        feedback.append("Hips too high! Lower your body!")
    elif hip[1] > knee[1] + 10:  
        feedback.append("Hips too low! Keep core tight!")
    elif spine_angle < 165 or spine_angle > 180:
        feedback.append("Maintain a neutral spine!")

    if elbow_angle > 160:
        feedback.append("Lower your chest more!")
    elif elbow_angle < 90:
        feedback.append("Don't go too low!")

    shoulder_elbow_diff = abs(shoulder[1] - elbow[1])
    if shoulder_elbow_diff < 10:
        feedback.append("Elbows too flared! Keep them closer!")

    chest = (shoulder + hip) / 2  

    if chest[1] > elbow[1] and elbow_angle < 90 and rep_status == "Up":  
        rep_status = "Down"  
    elif chest[1] < elbow[1] and elbow_angle > 160 and rep_status == "Down":  
        rep_status = "Up"  
        rep_count += 1  

    return " | ".join(feedback) if feedback else "Good push-up!", rep_count, rep_status

def process_pushup_video(video_source):
    return process_video(video_source)
