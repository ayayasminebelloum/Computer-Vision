# 1. Importing necessary libraries:
import numpy as np
import cv2
import time

# 2. Importing custom utility functions for gaze tracking and UI handling:
from gaze_tracking import GazeTracking
from utils.ui_utils import (
    get_screen_resolution,
    draw_text_lines,
    init_fullscreen_window,
    WINDOW_NAME
)

# 3. A function for estimating the distance between the user's eyes based on pupil positions:
def estimate_distance(gaze_tracking):
    left_pupil = gaze_tracking.pupil_left_coords()
    right_pupil = gaze_tracking.pupil_right_coords()

    # 3.1 - If both pupils are detected, calculate the Euclidean distance:
    if left_pupil and right_pupil:
        return np.linalg.norm(np.array(left_pupil) - np.array(right_pupil))

    # 3.2 - Returning None if one or both pupils are not detected.
    return None

# ----------------------------------------------------------------------------
#  4. Camera Calibration Function:
#     - gaze calibration process using predefined (relative) screen points
# ----------------------------------------------------------------------------
def calibrate_gaze(gaze_tracking, screen_width, screen_height, window_name):

    # 4.1 - Storing the pre-define calibration points as normalized (x, y) ratios of screen dimensions:
    calibration_points = [
        (0.1, 0.1), (0.5, 0.1), (0.9, 0.1),
        (0.1, 0.5), (0.5, 0.5), (0.9, 0.5),
        (0.1, 0.9), (0.5, 0.9), (0.9, 0.9)
    ]

    # 4.2 - Variable Initialization:
    calibration_data = [] # 4.2.1 - variable for storing the mapping between screen points and gaze data.
    distances = [] # 4.2.2 - variable for storing the estimated eye distances for each point.

    # 4.3 - Opening the webcam & Switching to a fullscreen window for calibration:
    webcam = cv2.VideoCapture(0)
    init_fullscreen_window()

    # 4.4 - Looping through each calibration point:
    for point in calibration_points:
        x, y = int(point[0] * screen_width), int(point[1] * screen_height)
        img = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        cv2.circle(img, (x, y), 15, (0, 255, 0), -1) # 4.4.1 - Drawing a green dot at the calibration point coordinates.

        gaze_points = []
        start_time = time.time()

        # 4.4.2 - Collecting gaze data from the user, 2 seconds per point:
        while time.time() - start_time < 2:
            ret, frame = webcam.read()
            if ret:
                gaze_tracking.refresh(frame)
                horizontal_ratio = gaze_tracking.horizontal_ratio()
                vertical_ratio = gaze_tracking.vertical_ratio()
                distance = estimate_distance(gaze_tracking)

                # 4.4.3 - If gaze and distance are valid --> storing the data:
                if horizontal_ratio is not None and vertical_ratio is not None and distance is not None:
                    gaze_points.append((horizontal_ratio, vertical_ratio))
                    distances.append(distance)

            cv2.imshow(window_name, img)
            if cv2.waitKey(1) == 27:
                break # ESC to cancel.

        # 4.4.4 -  Storing averaged gaze and distance for each calibration point:
        if gaze_points:
            avg_gaze = np.mean(gaze_points, axis=0)
            avg_distance = np.mean(distances)
            calibration_data.append((point, avg_gaze, avg_distance))
            print(f"Calibration point {point}: average gaze {avg_gaze}, average distance {avg_distance}")

    webcam.release()
    cv2.destroyWindow(window_name)

    # Error Handling --> Requiring minimum calibration data to compute transformation matrix:
    if len(calibration_data) < 4:
        print("Not enough calibration data collected.")
        return None, None

    # 4.4.5 - Extracting screen coordinates and corresponding gaze data:
    src_points = np.array([data[1] for data in calibration_data], dtype=np.float32)
    dst_points = np.array([data[0] for data in calibration_data], dtype=np.float32)

    # 4.4.6 - Computing transformation matrix from gaze space to screen space:
    transformation_matrix, _ = cv2.findHomography(src_points, dst_points)

    # 4.4.7 - Computing average user distance for later scaling:
    avg_distance = np.mean([data[2] for data in calibration_data])
    return transformation_matrix, avg_distance

# 5. A function for displaying instructions and initiating the calibration process:
def run_calibration(window_name="Gaze Tracker"):
    screen_width, screen_height = get_screen_resolution() # 5.1 - Getting screen dimensions.

    # 5.2 - Instructions text for the users:
    instruction_text = [
        "Calibration is required for each new user!",
        "",
        "Place your head at a comfortable distance from the screen.",
        "Make sure your face is well-lit and visible.",
        "",
        "Follow the green dots on screen, with your eyes ONLY.",
        "Try to keep your head still during calibration.",
        "",
        "Press any key to begin..."
    ]

    # 5.3 - Displaying the instructions on the users screen:
    canvas = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
    draw_text_lines(canvas, instruction_text, 200)
    init_fullscreen_window()
    cv2.imshow(window_name, canvas)
    cv2.waitKey(0)

    # 5.4 - Starting --> gaze calibration:
    gaze_tracking = GazeTracking()
    transformation_matrix, avg_distance = calibrate_gaze(gaze_tracking, screen_width, screen_height, window_name)
    return transformation_matrix, avg_distance, gaze_tracking
