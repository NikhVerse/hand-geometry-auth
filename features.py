import numpy as np
from typing import List, Tuple
from utils import euclidean_distance, calculate_angle, normalize_landmarks

def extract_features(raw_landmarks: List[Tuple[float, float]]) -> List[float]:
    """
    Extracts a robust geometric and statistical embedding from 21 MediaPipe hand landmarks.
    
    MediaPipe Landmark indices:
    0: Wrist
    1-4: Thumb
    5-8: Index
    9-12: Middle
    13-16: Ring
    17-20: Pinky
    
    Returns:
        List[float]: A 1D feature vector of size ~30.
    """
    if len(raw_landmarks) != 21:
        raise ValueError("Exactly 21 landmarks are required.")
    
    # 1. Normalize landmarks (Translate wrist to 0,0)
    landmarks = normalize_landmarks(raw_landmarks)
    
    features = []
    
    # 2. Extract Distance Features
    # Palm width (index base to pinky base)
    palm_width = euclidean_distance(landmarks[5], landmarks[17])
    # Add small epsilon to prevent division by zero
    palm_width = max(palm_width, 1e-6)
    
    # Finger lengths (tip to base)
    thumb_len = euclidean_distance(landmarks[4], landmarks[1])
    index_len = euclidean_distance(landmarks[8], landmarks[5])
    middle_len = euclidean_distance(landmarks[12], landmarks[9])
    ring_len = euclidean_distance(landmarks[16], landmarks[13])
    pinky_len = euclidean_distance(landmarks[20], landmarks[17])
    
    finger_lengths = [thumb_len, index_len, middle_len, ring_len, pinky_len]
    
    # 3. Ratio Features (Scale Invariant)
    # Normalize lengths by palm width
    normalized_lengths = [l / palm_width for l in finger_lengths]
    features.extend(normalized_lengths)
    
    # Wrist to fingertip distances normalized by palm width
    wrist_to_tips = [
        euclidean_distance(landmarks[0], landmarks[4]) / palm_width,
        euclidean_distance(landmarks[0], landmarks[8]) / palm_width,
        euclidean_distance(landmarks[0], landmarks[12]) / palm_width,
        euclidean_distance(landmarks[0], landmarks[16]) / palm_width,
        euclidean_distance(landmarks[0], landmarks[20]) / palm_width,
    ]
    features.extend(wrist_to_tips)
    
    # Distance between adjacent fingertips normalized
    tip_distances = [
        euclidean_distance(landmarks[4], landmarks[8]) / palm_width,
        euclidean_distance(landmarks[8], landmarks[12]) / palm_width,
        euclidean_distance(landmarks[12], landmarks[16]) / palm_width,
        euclidean_distance(landmarks[16], landmarks[20]) / palm_width,
    ]
    features.extend(tip_distances)

    # 4. Angular Features
    # Angles between wrist, finger base, and finger tip
    angles = [
        calculate_angle(landmarks[0], landmarks[1], landmarks[4]),    # Thumb
        calculate_angle(landmarks[0], landmarks[5], landmarks[8]),    # Index
        calculate_angle(landmarks[0], landmarks[9], landmarks[12]),   # Middle
        calculate_angle(landmarks[0], landmarks[13], landmarks[16]),  # Ring
        calculate_angle(landmarks[0], landmarks[17], landmarks[20]),  # Pinky
        
        # Angles between adjacent finger bases from wrist
        calculate_angle(landmarks[5], landmarks[0], landmarks[9]),    # Index-Wrist-Middle
        calculate_angle(landmarks[9], landmarks[0], landmarks[13]),   # Middle-Wrist-Ring
        calculate_angle(landmarks[13], landmarks[0], landmarks[17])   # Ring-Wrist-Pinky
    ]
    # Normalize angles to [0, 1] by dividing by 180
    normalized_angles = [a / 180.0 for a in angles]
    features.extend(normalized_angles)
    
    # 5. Statistical Features
    # Compute distances of all 20 points from wrist
    all_distances = [euclidean_distance(landmarks[0], lm) for lm in landmarks[1:]]
    normalized_all_distances = [d / palm_width for d in all_distances]
    
    mean_dist = np.mean(normalized_all_distances)
    var_dist = np.var(normalized_all_distances)
    
    features.extend([mean_dist, var_dist])
    
    # We now have an embedding of size 5 + 5 + 4 + 8 + 2 = 24 features
    # Ensure they are native floats, not numpy floats, for JSON serialization
    return [float(f) for f in features]
