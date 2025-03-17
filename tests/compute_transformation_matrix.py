# Run Command: python Test_scripts/compute_transformation_matrix.py
import numpy as np
import cv2

def compute_transformation_matrix(calibration_data):
    if len(calibration_data) < 4:
        raise ValueError("Not enough calibration data points to compute transformation matrix.")
    src_points = np.array([data[1] for data in calibration_data], dtype=np.float32)
    dst_points = np.array([data[0] for data in calibration_data], dtype=np.float32)
    transformation_matrix, _ = cv2.findHomography(src_points, dst_points, method=cv2.RANSAC)
    return transformation_matrix

def test_compute_transformation_matrix():
    calibration_data = [
        ((0.1, 0.1), (100, 100)),
        ((0.9, 0.1), (900, 100)),
        ((0.1, 0.9), (100, 900)),
        ((0.9, 0.9), (900, 900))
    ]
    transformation_matrix = compute_transformation_matrix(calibration_data)
    
    # Check if transformation matrix is generated
    assert transformation_matrix is not None, "Transformation matrix should not be None"
    assert transformation_matrix.shape == (3, 3), f"Expected transformation matrix shape to be (3, 3), but got {transformation_matrix.shape}"
    
    print(f"Transformation matrix:\n{transformation_matrix}")
    print("test_compute_transformation_matrix passed.")

if __name__ == "__main__":
    test_compute_transformation_matrix()