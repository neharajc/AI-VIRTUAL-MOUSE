import cv2
import dlib
import numpy as np
import pyautogui
import time

# Initialize dlib's face detector and facial landmarks predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

cap = cv2.VideoCapture(0)


def eye_aspect_ratio(eye):
    """Calculate the Eye Aspect Ratio (EAR) to detect blink."""
    vertical1 = np.linalg.norm(eye[1] - eye[5])
    vertical2 = np.linalg.norm(eye[2] - eye[4])
    horizontal = np.linalg.norm(eye[0] - eye[3])
    return (vertical1 + vertical2) / (2.0 * horizontal)


EAR_THRESHOLD = 0.25
LONG_BLINK_FRAMES = 8
DOUBLE_BLINK_FRAMES = 3
BLINK_COOLDOWN = 0.5  # seconds

frame_counter = 0
blink_counter = 0
last_blink_time = 0

try:
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)

            # Calculate EAR
            left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
            right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0

            # Check for blink based on EAR
            if ear < EAR_THRESHOLD:
                frame_counter += 1
            else:
                # Long blink for left click
                if frame_counter >= LONG_BLINK_FRAMES:
                    pyautogui.click(button='left')
                    frame_counter = 0
                    blink_counter = 0
                # Short blink, potentially a part of a double blink
                elif frame_counter >= DOUBLE_BLINK_FRAMES:
                    blink_counter += 1
                    frame_counter = 0

                    # If second blink is too far from the first, reset counter
                    if time.time() - last_blink_time > BLINK_COOLDOWN:
                        blink_counter = 1

                    # Detect double blink
                    if blink_counter == 2:
                        pyautogui.click(button='right')
                        blink_counter = 0

                    last_blink_time = time.time()
                else:
                    frame_counter = 0

        cv2.imshow('Blink Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

cap.release()
cv2.destroyAllWindows()
