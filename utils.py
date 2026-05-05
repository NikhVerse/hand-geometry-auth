import math
import numpy as np
from typing import List, Tuple

def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculates Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_angle(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
    """
    Calculates the angle (in degrees) formed by three points p1, p2, p3.
    p2 is the vertex of the angle.
    """
    a = np.array(p1)
    b = np.array(p2)
    c = np.array(p3)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    
    # Handle floating point inaccuracies
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

def normalize_landmarks(landmarks: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Translates landmarks so that the wrist (landmark 0) is at the origin (0, 0).
    This provides translation invariance.
    """
    if not landmarks:
        return []
    
    wrist_x, wrist_y = landmarks[0]
    normalized = []
    
    for x, y in landmarks:
        normalized.append((x - wrist_x, y - wrist_y))
        
    return normalized
