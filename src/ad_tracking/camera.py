# 1. Importing necessary libraries:
import cv2
import numpy as np

# 2. Importing custom utility functions for gaze tracking and UI handling:
from gaze_tracking import GazeTracking
from ad_tracking.calibrate import estimate_distance
from utils.ui_utils import (
    init_fullscreen_window,
    detect_button_click,
    draw_exit_and_home,
    get_screen_resolution,
    WINDOW_NAME
)

# 3. A function for converting gaze ratios to screen coordinates using perspective transformation and distance scaling:
def map_gaze_to_screen(gaze_tracking, screen_width, screen_height, transformation_matrix, distance_factor):
    horizontal_ratio = gaze_tracking.horizontal_ratio()
    vertical_ratio = gaze_tracking.vertical_ratio()

    # 3.1 - Checking if both gaze ratios are valid:
    if horizontal_ratio is not None and vertical_ratio is not None:
        gaze_point = np.array([[horizontal_ratio, vertical_ratio]], dtype=np.float32).reshape(-1, 1, 2)
        screen_point = cv2.perspectiveTransform(gaze_point, transformation_matrix).reshape(-1, 2)[0]

        # 3.2 - Scaling and mapping to actual screen/pixel coordinates:
        screen_x = int(screen_point[0] * screen_width * distance_factor)
        screen_y = int(screen_point[1] * screen_height * distance_factor)
        return screen_x, screen_y

    # 3.3 - Returning None if gaze data is invalid.
    return None, None

# 4. A function for displaying a real-time webcam feed with gaze tracking overlay:
def show_live_coordinates(gaze_tracking, screen_width, screen_height, transformation_matrix, avg_distance, window_name="Gaze Tracker"):
    webcam = cv2.VideoCapture(0) # 4.1 - Opening webcam.
    init_fullscreen_window() # 4.2 - Entering fullscreen mode.

    clicked_code = [None]  # -1 = exit, -2 = home

    # 4.3 - Mouse click callback to detect which ad was clicked:
    def click_handler(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            result = detect_button_click(x, y, [], screen_width, screen_height, show_home_button=True)
            if result in [-1, -2]:
                clicked_code[0] = result

    cv2.setMouseCallback(WINDOW_NAME, click_handler) # 4.4 - Attaching mouse callback to window.

    # 4.5 - Main loop for real-time gaze tracking:
    while True:
        ret, frame = webcam.read()
        if not ret:
            break

        frame = cv2.resize(frame, (screen_width, screen_height)) # 4.5.1 - Resizing frame to match screen.
        gaze_tracking.refresh(frame) # 4.5.2 - Updating gaze tracking with current frame.

        distance = estimate_distance(gaze_tracking) # 4.5.3 - Estimating user's distance from screen.
        if distance is not None:
            distance_factor = avg_distance / distance # 4.5.4 -  Scaling based on distance.
            screen_x, screen_y = map_gaze_to_screen(gaze_tracking, screen_width, screen_height, transformation_matrix, distance_factor)

            # 4.5.5 - If valid screen coordinates, draw a green cross at the gaze point:
            if screen_x is not None and screen_y is not None:
                cv2.drawMarker(frame, (screen_x, screen_y), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=30, thickness=2)
                coord_text = f"Gaze Coordinates: ({screen_x}, {screen_y})"
                cv2.putText(frame, coord_text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.0, (147, 58, 31), 2)

        # 4.5.6 - Displaying live left and right pupil coordinates:
        left_pupil = gaze_tracking.pupil_left_coords()
        right_pupil = gaze_tracking.pupil_right_coords()
        cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        # 4.5.7 - Drawing exit and home buttons on the screen:
        draw_exit_and_home(frame, screen_width, screen_height, show_home_button=True)

        # 4.5.8 - Displaying frame:
        cv2.imshow(window_name, frame)

        if clicked_code[0] in [-1, -2] or cv2.waitKey(1) == 27:
            break # Breaking loop if ESC key or exit/home is clicked.

    webcam.release() # 4.6 - Releasing the webcam when done.
    cv2.destroyWindow(window_name) # 4.7 - Closing the window.
    return clicked_code[0] # 4.8 - Returning action code (e.g., -1 for exit).
