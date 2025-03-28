import numpy as np
import cv2
import os
import time
from ad_tracking.calibrate import estimate_distance
from utils.ui_utils import (
    get_screen_resolution,
    draw_exit_and_home,
    detect_button_click,
    init_fullscreen_window,
    WINDOW_NAME
)

def resize_to_fullscreen(img, screen_width, screen_height):
    return cv2.resize(img, (screen_width, screen_height), interpolation=cv2.INTER_LINEAR)

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

def create_heatmap(screen_height, screen_width):
    return np.zeros((screen_height, screen_width), dtype=np.float32)

def show_ad(ad_path, gaze_tracking, screen_width, screen_height, transformation_matrix, avg_distance, duration=10, window_name="Gaze Tracker"):
    ad_img = cv2.imread(ad_path)
    ad_img = resize_to_fullscreen(ad_img, screen_width, screen_height)
    heatmap = create_heatmap(screen_height, screen_width)

    webcam = cv2.VideoCapture(0)
    init_fullscreen_window()

    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = webcam.read()
        if not ret:
            break

        gaze_tracking.refresh(frame)
        distance = estimate_distance(gaze_tracking)
        if distance is not None:
            distance_factor = avg_distance / distance
            screen_x, screen_y = map_gaze_to_screen(
                gaze_tracking, screen_width, screen_height, transformation_matrix, distance_factor)
            if screen_x is not None and screen_y is not None:
                if 0 <= screen_x < screen_width and 0 <= screen_y < screen_height:
                    cv2.circle(heatmap, (screen_x, screen_y), 50, 1, -1)

        cv2.imshow(window_name, ad_img)
        if cv2.waitKey(1) == 27:
            break

    webcam.release()
    heatmap_blurred = cv2.GaussianBlur(heatmap, (101, 101), 0)
    return heatmap_blurred

def choose_ad(screen_width, screen_height, window_name="Gaze Tracker"):
    import glob

    ad_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    ad_files = sorted(glob.glob(os.path.join(ad_folder, "ad*.jp*g")))  # handles .jpg and .jpeg

    if not ad_files:
        print("No ad images found in the data folder.")
        return None

    thumbnails = [cv2.resize(cv2.imread(path), (300, 200)) for path in ad_files]
    selected = [None]

    def on_click(event, x, y, flags, param):
        for i in range(len(thumbnails)):
            row, col = divmod(i, 3)
            x_offset = col * 330 + 100
            y_offset = row * 230 + 150
            if x_offset <= x <= x_offset + 300 and y_offset <= y <= y_offset + 200:
                selected[0] = ad_files[i]
                return

    init_fullscreen_window()
    cv2.setMouseCallback(window_name, on_click)

    while selected[0] is None:
        canvas = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        canvas[:] = (20, 20, 20)
        cv2.putText(canvas, "Choose your ad", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

        for i, thumb in enumerate(thumbnails):
            row, col = divmod(i, 3)
            x_offset = col * 330 + 100
            y_offset = row * 230 + 150
            canvas[y_offset:y_offset + 200, x_offset:x_offset + 300] = thumb
            cv2.putText(canvas, f"Ad {i+1}", (x_offset + 90, y_offset + 190),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        draw_exit_and_home(canvas, screen_width, screen_height, show_home_button=True)
        cv2.imshow(window_name, canvas)

        if cv2.waitKey(1) == 27:
            break

    return selected[0]

def display_heatmap(heatmap, ad_path, screen_width, screen_height, window_name="Gaze Tracker"):
    ad_img = cv2.imread(ad_path)
    ad_img = resize_to_fullscreen(ad_img, screen_width, screen_height)
    heatmap_resized = cv2.resize(heatmap, (ad_img.shape[1], ad_img.shape[0]))

    heatmap_normalized = cv2.normalize(heatmap_resized, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_colored = cv2.applyColorMap(heatmap_normalized.astype(np.uint8), cv2.COLORMAP_JET)
    blended = cv2.addWeighted(ad_img, 0.5, heatmap_colored, 0.5, 0)

    while True:
        cv2.imshow(window_name, blended)
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyWindow(window_name)