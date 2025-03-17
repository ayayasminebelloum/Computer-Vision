# Run Command: python Test_scripts/calibrate_gaze.py
import numpy as np
import cv2
import time
from gaze_tracking import GazeTracking
from screeninfo import get_monitors

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
    print(f"Calibration data: {calibration_data}")
    return calibration_data

def test_calibrate_gaze():
    gaze_tracking = GazeTracking()
    window_width, window_height = 640, 480
    vertical_position = 100
    calibration_data = calibrate_gaze(gaze_tracking, window_width, window_height, vertical_position)
    
    # Check if calibration data is generated
    assert calibration_data is not None, "Calibration data should not be None"
    assert len(calibration_data) > 0, "Calibration data should not be empty"
    
    print(f"Calibration data: {calibration_data}")
    print("test_calibrate_gaze passed.")

if __name__ == "__main__":
    test_calibrate_gaze()