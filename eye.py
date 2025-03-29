import cv2
import dlib
import numpy as np
import pyautogui
import time

pyautogui.FAILSAFE = False  
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

def eye_aspect_ratio(eye):
    vertical1 = np.linalg.norm(eye[1] - eye[5])
    vertical2 = np.linalg.norm(eye[2] - eye[4])
    horizontal = np.linalg.norm(eye[0] - eye[3])
    return (vertical1 + vertical2) / (2.0 * horizontal)

def calibrate():
    input("Look at the center of the screen and press Enter...")
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if faces:
        landmarks = predictor(gray, faces[0])
        nose_position = (landmarks.part(33).x, landmarks.part(33).y)
        return nose_position
    else:
        print("❌ Face not detected during calibration. Try again.")
        return None

calibration_data = calibrate()
BLINK_THRESHOLD = 0.18  
EYE_CONSECUTIVE_FRAMES = 10  
BLINK_COOLDOWN = 1.0  

last_left_click = 0
last_right_click = 0
last_double_click = 0

if calibration_data:
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                landmarks = predictor(gray, face)

                # Cursor Movement using Nose Position
                nose_position = (landmarks.part(33).x, landmarks.part(33).y)
                diff_x = (nose_position[0] - calibration_data[0]) * 3  
                diff_y = (nose_position[1] - calibration_data[1]) * 3  

                # Ensure Cursor Stays Fully Inside the Screen
                cursor_x = np.clip(pyautogui.position()[0] + diff_x, 0, screen_w - 1)
                cursor_y = np.clip(pyautogui.position()[1] + diff_y, 0, screen_h - 1)
                pyautogui.moveTo(cursor_x, cursor_y, duration=0.1)

                # Blink Detection
                left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
                right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)

                current_time = time.time()

                # Left Blink → Left Click
                if left_ear < BLINK_THRESHOLD and right_ear > BLINK_THRESHOLD:
                    if current_time - last_left_click > BLINK_COOLDOWN:
                        pyautogui.click(button='left')
                        last_left_click = current_time
                        print("✅ Left Click")

                # Right Blink → Right Click
                if right_ear < BLINK_THRESHOLD and left_ear > BLINK_THRESHOLD:
                    if current_time - last_right_click > BLINK_COOLDOWN:
                        pyautogui.click(button='right')
                        last_right_click = current_time
                        print("✅ Right Click")

                # Both Blinks → Double Click
                if left_ear < BLINK_THRESHOLD and right_ear < BLINK_THRESHOLD:
                    if current_time - last_double_click > BLINK_COOLDOWN:
                        pyautogui.doubleClick()
                        last_double_click = current_time
                        print("✅ Double Click")

            cv2.imshow('Eye Controlled Mouse', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass

    cap.release()
    cv2.destroyAllWindows()