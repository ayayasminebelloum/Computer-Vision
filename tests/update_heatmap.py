# Run Command: python Test_scripts/update_heatmap.py
import numpy as np
import cv2
import matplotlib.pyplot as plt

def create_heatmap(ad_size):
    return np.zeros((ad_size[0], ad_size[1]))

def map_gaze_to_grid(gaze_x, gaze_y, webcam_size, ad_size, transformation_matrix):
    raw_point = np.array([[gaze_x, gaze_y]], dtype=np.float32).reshape(-1, 1, 2)
    transformed_point = cv2.perspectiveTransform(raw_point, transformation_matrix).reshape(-1, 2)[0]
    flipped_gaze_y = webcam_size[1] - transformed_point[1]
    ad_x = int((transformed_point[0] / webcam_size[0]) * ad_size[1])
    ad_y = int((flipped_gaze_y / webcam_size[1]) * ad_size[0])
    return ad_x, ad_y

def update_heatmap(heatmap, gaze_x, gaze_y, webcam_size, ad_size, transformation_matrix):
    if gaze_x is not None and gaze_y is not None:
        ad_x, ad_y = map_gaze_to_grid(gaze_x, gaze_y, webcam_size, ad_size, transformation_matrix)
        ad_x_int = min(max(int(ad_x), 0), ad_size[1] - 1)
        ad_y_int = min(max(int(ad_y), 0), ad_size[0] - 1)
        cv2.circle(heatmap, (ad_x_int, ad_y_int), 10, 1, -1)
    return heatmap

def test_update_heatmap():
    ad_size = (1080, 1920)
    heatmap = create_heatmap(ad_size)
    gaze_x, gaze_y = 320, 240
    webcam_size = (640, 480)
    transformation_matrix = np.eye(3)
    heatmap = update_heatmap(heatmap, gaze_x, gaze_y, webcam_size, ad_size, transformation_matrix)
    
    # Expected values
    expected_ad_x = int((gaze_x / webcam_size[0]) * ad_size[1])
    expected_ad_y = int(((webcam_size[1] - gaze_y) / webcam_size[1]) * ad_size[0])
    ad_x_int = min(max(int(expected_ad_x), 0), ad_size[1] - 1)
    ad_y_int = min(max(int(expected_ad_y), 0), ad_size[0] - 1)
    
    assert heatmap[ad_y_int, ad_x_int] == 1, f"Expected heatmap at ({ad_y_int}, {ad_x_int}) to be 1, but got {heatmap[ad_y_int, ad_x_int]}"
    
    print("test_update_heatmap passed.")
    plt.imshow(heatmap, cmap="hot", interpolation="nearest")
    plt.show()

if __name__ == "__main__":
    test_update_heatmap()