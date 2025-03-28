import cv2
import numpy as np
from gaze_tracking import GazeTracking
from ad_tracking.calibrate import estimate_distance
from utils.ui_utils import (
    init_fullscreen_window,
    detect_button_click,
    draw_exit_and_home,
    get_screen_resolution,
    WINDOW_NAME
)

# Map gaze to screen coordinates
def map_gaze_to_screen(gaze_tracking, screen_width, screen_height, transformation_matrix, distance_factor):
    horizontal_ratio = gaze_tracking.horizontal_ratio()
    vertical_ratio = gaze_tracking.vertical_ratio()
    if horizontal_ratio is not None and vertical_ratio is not None:
        gaze_point = np.array([[horizontal_ratio, vertical_ratio]], dtype=np.float32).reshape(-1, 1, 2)
        screen_point = cv2.perspectiveTransform(gaze_point, transformation_matrix).reshape(-1, 2)[0]
        screen_x = int(screen_point[0] * screen_width * distance_factor)
        screen_y = int(screen_point[1] * screen_height * distance_factor)
        return screen_x, screen_y
    return None, None

# Show real-time gaze tracking webcam feed with crosshair at gaze point
def show_live_coordinates(gaze_tracking, screen_width, screen_height, transformation_matrix, avg_distance, window_name="Gaze Tracker"):
    webcam = cv2.VideoCapture(0)
    init_fullscreen_window()

    clicked_code = [None]  # -1 = exit, -2 = home

    def click_handler(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            result = detect_button_click(x, y, [], screen_width, screen_height, show_home_button=True)
            if result in [-1, -2]:
                clicked_code[0] = result

    cv2.setMouseCallback(WINDOW_NAME, click_handler)

    while True:
        ret, frame = webcam.read()
        if not ret:
            break

        frame = cv2.resize(frame, (screen_width, screen_height))
        gaze_tracking.refresh(frame)

        distance = estimate_distance(gaze_tracking)
        if distance is not None:
            distance_factor = avg_distance / distance
            screen_x, screen_y = map_gaze_to_screen(gaze_tracking, screen_width, screen_height, transformation_matrix, distance_factor)
            if screen_x is not None and screen_y is not None:
                # Draw green cross marker where the user is looking
                cv2.drawMarker(frame, (screen_x, screen_y), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=30, thickness=2)
                coord_text = f"Gaze Coordinates: ({screen_x}, {screen_y})"
                cv2.putText(frame, coord_text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.0, (147, 58, 31), 2)

        # Display pupil coordinates
        left_pupil = gaze_tracking.pupil_left_coords()
        right_pupil = gaze_tracking.pupil_right_coords()
        cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        draw_exit_and_home(frame, screen_width, screen_height, show_home_button=True)
        cv2.imshow(window_name, frame)

        if clicked_code[0] in [-1, -2] or cv2.waitKey(1) == 27:
            break

    webcam.release()
    cv2.destroyWindow(window_name)
    return clicked_code[0]