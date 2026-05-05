import cv2
import mediapipe as mp
import numpy as np
import base64
from typing import List, Tuple

mp_hands = mp.solutions.hands
# Using static_image_mode=True because we process independent frames from the API
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

def decode_image(base64_string: str) -> np.ndarray:
    """Decodes a base64 string to an OpenCV BGR image."""
    # Remove header if present (e.g., data:image/jpeg;base64,)
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def process_frame(base64_string: str) -> List[Tuple[float, float]]:
    """
    Processes a base64 encoded image, detects a hand, and extracts landmarks.
    
    Returns:
        A list of 21 (x, y) tuples representing hand landmarks.
        
    Raises:
        ValueError: If no hand is detected, or multiple hands are detected.
    """
    img = decode_image(base64_string)
    if img is None:
        raise ValueError("Invalid image data.")
        
    # Convert BGR to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    results = hands.process(img_rgb)
    
    if not results.multi_hand_landmarks:
        raise ValueError("No hand detected.")
        
    if len(results.multi_hand_landmarks) > 1:
        raise ValueError("Multiple hands detected. Please present only one hand.")
        
    hand_landmarks = results.multi_hand_landmarks[0]
    
    # Extract normalized coordinates (x, y)
    landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
    
    return landmarks
