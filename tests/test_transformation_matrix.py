import numpy as np
import cv2

# Dummy screen resolution
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Simulated test data: raw gaze ratios and expected screen points
# Format: (horizontal_ratio, vertical_ratio) -> (expected_x_ratio, expected_y_ratio)
test_cases = [
    ((0.1, 0.1), (0.1, 0.1)),
    ((0.5, 0.1), (0.5, 0.1)),
    ((0.9, 0.1), (0.9, 0.1)),
    ((0.1, 0.5), (0.1, 0.5)),
    ((0.5, 0.5), (0.5, 0.5)),
    ((0.9, 0.5), (0.9, 0.5)),
    ((0.1, 0.9), (0.1, 0.9)),
    ((0.5, 0.9), (0.5, 0.9)),
    ((0.9, 0.9), (0.9, 0.9)),
]

# Simulated calibration data (you would normally get this from your actual calibration)
raw_points = np.array([case[0] for case in test_cases], dtype=np.float32)
target_points = np.array([case[1] for case in test_cases], dtype=np.float32)

# Compute transformation matrix
transformation_matrix, _ = cv2.findHomography(raw_points, target_points)

# Function to apply transformation
def apply_transformation(point, matrix):
    point = np.array([[point]], dtype=np.float32)  # shape: (1,1,2)
    transformed = cv2.perspectiveTransform(point, matrix)
    return transformed[0][0]

# Test each case
print("🔍 Testing transformation matrix:")
for i, (raw, expected) in enumerate(test_cases):
    transformed = apply_transformation(raw, transformation_matrix)
    transformed_screen = (transformed[0] * SCREEN_WIDTH, transformed[1] * SCREEN_HEIGHT)
    expected_screen = (expected[0] * SCREEN_WIDTH, expected[1] * SCREEN_HEIGHT)
    error = np.linalg.norm(np.array(transformed_screen) - np.array(expected_screen))
    print(f"Test {i+1}: Raw {raw} -> Screen {transformed_screen} | Expected {expected_screen} | Error: {error:.2f}")