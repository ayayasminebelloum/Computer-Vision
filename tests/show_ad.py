# Run Command: python Test_scripts/update_heatmap.py
import numpy as np
import cv2
import os
from gaze_tracking import GazeTracking
from screeninfo import get_monitors

def create_heatmap(ad_size):
    return np.zeros((ad_size[0], ad_size[1]))

def get_screen_resolution():
    monitor = get_monitors()[0]
    return monitor.width, monitor.height

def calibrate_gaze(gaze_tracking, window_width, window_height, vertical_position):
    calibration_points = [
        (0.1, 0.1), (0.5, 0.1), (0.9, 0.1),
        (0.1, 0.5), (0.5, 0.5), (0.9, 0.5),
        (0.1, 0.9), (0.5, 0.9), (0.9, 0.9)
    ]
    calibration_data = []
    cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Calibration", window_width, window_height)
    screen_width, screen_height = get_screen_resolution()
    cv2.moveWindow("Calibration", (screen_width - window_width) // 2, vertical_position)
    webcam = cv2.VideoCapture(0)
    for point in calibration_points:
        img = np.zeros((window_height, window_width, 3), dtype=np.uint8)
        x = int(point[0] * window_width)
        y = int(point[1] * window_height)
        cv2.circle(img, (x, y), 10, (0, 255, 0), -1)
        start_time = time.time()
        while time.time() - start_time < 2:
            cv2.imshow("Calibration", img)
            ret, frame = webcam.read()
            if ret:
                gaze_tracking.refresh(frame)
                left_pupil = gaze_tracking.pupil_left_coords()
                right_pupil = gaze_tracking.pupil_right_coords()
                if left_pupil and right_pupil:
                    gaze_x = (left_pupil[0] + right_pupil[0]) / 2
                    gaze_y = (left_pupil[1] + right_pupil[1]) / 2
                    calibration_data.append((point, (gaze_x, gaze_y)))
            if cv2.waitKey(1) == 27:
                break
    webcam.release()
    cv2.destroyWindow("Calibration")
    return calibration_data

def compute_transformation_matrix(calibration_data):
    if len(calibration_data) < 4:
        raise ValueError("Not enough calibration data points to compute transformation matrix.")
    src_points = np.array([data[1] for data in calibration_data], dtype=np.float32)
    dst_points = np.array([data[0] for data in calibration_data], dtype=np.float32)
    transformation_matrix, _ = cv2.findHomography(src_points, dst_points, method=cv2.RANSAC)
    return transformation_matrix

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

def show_ad(ad_path, gaze_tracking):
    frame = cv2.imread(ad_path)
    heatmap = create_heatmap(frame.shape)
    ad_height, ad_width, _ = frame.shape
    webcam = cv2.VideoCapture(0)
    webcam_width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
    webcam_height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    webcam_size = (webcam_width, webcam_height)
    ad_size = (ad_height, ad_width)
    screen_width, screen_height = get_screen_resolution()
    window_width = frame.shape[1]
    window_height = frame.shape[0]
    window_width = int(window_width * 0.5)
    window_height = int(window_height * 0.5)
    window_width = min(window_width, screen_width)
    window_height = min(window_height, screen_height)
    top_distance = 50
    bottom_distance = 50
    vertical_position = (screen_height - window_height - top_distance - bottom_distance) // 2 + top_distance
    calibration_data = calibrate_gaze(gaze_tracking, window_width, window_height, vertical_position)
    transformation_matrix = compute_transformation_matrix(calibration_data)
    start_time = time.time()
    while time.time() - start_time < 10:
        ret, webcam_frame = webcam.read()
        gaze_tracking.refresh(webcam_frame)
        left_pupil = gaze_tracking.pupil_left_coords()
        right_pupil = gaze_tracking.pupil_right_coords()
        if left_pupil:
            heatmap = update_heatmap(heatmap, left_pupil[0], left_pupil[1], webcam_size, ad_size, transformation_matrix)
        if right_pupil:
            heatmap = update_heatmap(heatmap, right_pupil[0], right_pupil[1], webcam_size, ad_size, transformation_matrix)
        cv2.namedWindow("Ad Display", cv2.WINDOW_NORMAL)
        cv2.imshow("Ad Display", frame)
        cv2.resizeWindow("Ad Display", window_width, window_height)
        cv2.moveWindow("Ad Display", (screen_width - window_width) // 2, vertical_position)
        if cv2.waitKey(1) == 27:
            break
    webcam.release()
    cv2.destroyAllWindows()
    return heatmap

def test_show_ad():
    gaze_tracking = GazeTracking()
    ad_path = os.path.join('AdImages', 'PHOTO-2025-03-02-09-10-01.jpg')
    heatmap = show_ad(ad_path, gaze_tracking)
    
    # Check if heatmap is generated
    assert heatmap is not None, "Heatmap should not be None"
    assert heatmap.shape == (1080, 1920), f"Expected heatmap shape to be (1080, 1920), but got {heatmap.shape}"
    
    print("test_show_ad passed.")

if __name__ == "__main__":
    test_show_ad()