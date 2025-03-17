# Run Command: python Test_scripts/map_gaze_to_grid.py
import numpy as np
import cv2

def map_gaze_to_grid(gaze_x, gaze_y, webcam_size, ad_size, transformation_matrix):
    raw_point = np.array([[gaze_x, gaze_y]], dtype=np.float32).reshape(-1, 1, 2)
    transformed_point = cv2.perspectiveTransform(raw_point, transformation_matrix).reshape(-1, 2)[0]
    flipped_gaze_y = webcam_size[1] - transformed_point[1]
    ad_x = int((transformed_point[0] / webcam_size[0]) * ad_size[1])
    ad_y = int((flipped_gaze_y / webcam_size[1]) * ad_size[0])
    return ad_x, ad_y

def test_map_gaze_to_grid():
    gaze_x, gaze_y = 320, 240
    webcam_size = (640, 480)
    ad_size = (1080, 1920)
    transformation_matrix = np.eye(3)
    ad_x, ad_y = map_gaze_to_grid(gaze_x, gaze_y, webcam_size, ad_size, transformation_matrix)
    
    # Expected values based on the identity transformation matrix
    expected_ad_x = int((gaze_x / webcam_size[0]) * ad_size[1])
    expected_ad_y = int(((webcam_size[1] - gaze_y) / webcam_size[1]) * ad_size[0])
    
    assert ad_x == expected_ad_x, f"Expected ad_x to be {expected_ad_x}, but got {ad_x}"
    assert ad_y == expected_ad_y, f"Expected ad_y to be {expected_ad_y}, but got {ad_y}"
    
    print("test_map_gaze_to_grid passed.")

if __name__ == "__main__":
    test_map_gaze_to_grid()