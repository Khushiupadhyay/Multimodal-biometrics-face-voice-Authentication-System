import numpy as np
import cv2

def test(image, model_dir, device_id):
    print(f"Running face anti-spoofing test with model: {model_dir}")

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Fake detection logic (Replace this with actual ML model)
    if np.mean(gray) > 100:  # Arbitrary threshold
        return 1  # Real face
    else:
        return 0  # Spoofed face
