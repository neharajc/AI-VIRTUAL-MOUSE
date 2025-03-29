import tkinter as tk
from tkinter import ttk
import cv2
import mediapipe as mp
import pyautogui
import threading
import time

class GestureControlGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gesture Control Interface")
        self.root.geometry("800x600")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        self.setup_gui()
        self.running = False
        
    def setup_gui(self):
        # Create main frames
        self.control_frame = ttk.Frame(self.root, padding="10")
        self.control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.status_frame = ttk.Frame(self.root, padding="10")
        self.status_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons
        self.start_button = ttk.Button(self.control_frame, text="Start", command=self.start_tracking)
        self.start_button.grid(row=0, column=0, pady=5)
        
        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=self.stop_tracking)
        self.stop_button.grid(row=1, column=0, pady=5)
        
        # Status display
        self.status_label = ttk.Label(self.status_frame, text="Status: Not Running")
        self.status_label.grid(row=0, column=0, pady=5)
        
        self.gesture_label = ttk.Label(self.status_frame, text="Gesture: None")
        self.gesture_label.grid(row=1, column=0, pady=5)
        
        # Gesture guide
        self.guide_frame = ttk.LabelFrame(self.control_frame, text="Gesture Guide", padding="10")
        self.guide_frame.grid(row=2, column=0, pady=10)
        
        gestures = {
            "V_GEST": "Left/Right Click",
            "FIST": "Drag",
            "MID": "Click",
            "INDEX": "Right Click",
            "TWO_FINGER_CLOSED": "Double Click",
            "PINCH_MINOR": "Scroll",
            "PINCH_MAJOR": "Brightness/Volume"
        }
        
        for i, (gesture, action) in enumerate(gestures.items()):
            ttk.Label(self.guide_frame, text=f"{gesture}: {action}").grid(row=i, column=0, sticky=tk.W)
        
    def start_tracking(self):
        if not self.running:
            self.running = True
            self.start_button.state(['disabled'])
            self.status_label.config(text="Status: Running")
            self.tracking_thread = threading.Thread(target=self.track_gestures)
            self.tracking_thread.start()
    
    def stop_tracking(self):
        if self.running:
            self.running = False
            self.start_button.state(['!disabled'])
            self.status_label.config(text="Status: Not Running")
            if hasattr(self, 'tracking_thread'):
                self.tracking_thread.join()
    
    def track_gestures(self):
        while self.running:
            success, image = self.cap.read()
            if not success:
                continue
                
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = self.hands.process(image)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Update gesture label
                    gesture = self.get_gesture(hand_landmarks)
                    self.gesture_label.config(text=f"Gesture: {gesture}")
                    
                    # Process gesture
                    self.process_gesture(gesture, hand_landmarks)
                    
                    # Draw landmarks
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    self.mp_drawing = mp.solutions.drawing_utils
                    self.mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                        self.mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
                    )
            
            cv2.imshow('Gesture Control', image)
            if cv2.waitKey(5) & 0xFF == 27:  # Escape to exit
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
    
    def get_gesture(self, hand_landmarks):
        # Implement your gesture recognition logic here
        return "Unknown"
    
    def process_gesture(self, gesture, hand_landmarks):
        # Implement your gesture processing logic here
        pass
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = GestureControlGUI()
    gui.run()