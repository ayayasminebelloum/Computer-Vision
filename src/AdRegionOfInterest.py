import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import time
from gaze_tracking import GazeTracking
from screeninfo import get_monitors

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

def get_screen_resolution():
    monitor = get_monitors()[0]
    resolution = (monitor.width, monitor.height)
    print(f"Screen resolution: {resolution}")
    return resolution

def create_heatmap(screen_height, screen_width):
    print(f"Creating heatmap of size: ({screen_height}, {screen_width})")
    return np.zeros((screen_height, screen_width), dtype=np.float32)

def estimate_distance(gaze_tracking):
    left_pupil = gaze_tracking.pupil_left_coords()
    right_pupil = gaze_tracking.pupil_right_coords()
    if left_pupil and right_pupil:
        distance = np.linalg.norm(np.array(left_pupil) - np.array(right_pupil))
        return distance
    return None

def calibrate_gaze(gaze_tracking, screen_width, screen_height):
    calibration_points = [
        (0.1, 0.1), (0.5, 0.1), (0.9, 0.1),
        (0.1, 0.5), (0.5, 0.5), (0.9, 0.5),
        (0.1, 0.9), (0.5, 0.9), (0.9, 0.9)
    ]
    calibration_data = []
    distances = []
    webcam = cv2.VideoCapture(0)

    cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Calibration", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    for point in calibration_points:
        x, y = int(point[0] * screen_width), int(point[1] * screen_height)
        img = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        cv2.circle(img, (x, y), 15, (0, 255, 0), -1)

        gaze_points = []
        start_time = time.time()
        while time.time() - start_time < 2:
            ret, frame = webcam.read()
            if ret:
                gaze_tracking.refresh(frame)
                horizontal_ratio = gaze_tracking.horizontal_ratio()
                vertical_ratio = gaze_tracking.vertical_ratio()
                distance = estimate_distance(gaze_tracking)
                if horizontal_ratio is not None and vertical_ratio is not None and distance is not None:
                    gaze_points.append((horizontal_ratio, vertical_ratio))
                    distances.append(distance)

            cv2.imshow("Calibration", img)
            if cv2.waitKey(1) == 27:
                break

        if gaze_points:
            avg_gaze = np.mean(gaze_points, axis=0)
            avg_distance = np.mean(distances)
            calibration_data.append((point, avg_gaze, avg_distance))
            print(f"Calibration point {point}: average gaze {avg_gaze}, average distance {avg_distance}")

    webcam.release()
    cv2.destroyWindow("Calibration")
    print("Calibration completed with data:", calibration_data)

    # Compute the transformation matrix using findHomography
    src_points = np.array([data[1] for data in calibration_data], dtype=np.float32)
    dst_points = np.array([data[0] for data in calibration_data], dtype=np.float32)
    transformation_matrix, _ = cv2.findHomography(src_points, dst_points)
    avg_distance = np.mean([data[2] for data in calibration_data])
    return transformation_matrix, avg_distance

def show_ad(ad_path, gaze_tracking, screen_width, screen_height, transformation_matrix, avg_distance, duration=10):
    ad_img = cv2.imread(ad_path)
    ad_img = cv2.resize(ad_img, (screen_width, screen_height))
    heatmap = create_heatmap(screen_height, screen_width)

    webcam = cv2.VideoCapture(0)
    cv2.namedWindow("Ad Display", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Ad Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = webcam.read()
        if ret:
            gaze_tracking.refresh(frame)
            distance = estimate_distance(gaze_tracking)
            if distance is not None:
                distance_factor = avg_distance / distance
                screen_x, screen_y = map_gaze_to_screen(gaze_tracking, screen_width, screen_height, transformation_matrix, distance_factor)

                if screen_x is not None and screen_y is not None:
                    if 0 <= screen_x < screen_width and 0 <= screen_y < screen_height:
                        cv2.circle(heatmap, (screen_x, screen_y), 50, 1, -1)
                        print(f"Heatmap updated at ({screen_x}, {screen_y})")

        cv2.imshow("Ad Display", ad_img)
        if cv2.waitKey(1) == 27:
            break

    webcam.release()
    cv2.destroyAllWindows()
    heatmap_blurred = cv2.GaussianBlur(heatmap, (101, 101), 0)
    return heatmap_blurred

def display_heatmap(heatmap, ad_path, screen_width, screen_height):
    ad_img = cv2.imread(ad_path)
    ad_img = cv2.resize(ad_img, (screen_width, screen_height))
    ad_img = cv2.cvtColor(ad_img, cv2.COLOR_BGR2RGB)
    heatmap_resized = cv2.resize(heatmap, (ad_img.shape[1], ad_img.shape[0]))
    plt.figure(figsize=(12, 8))
    plt.imshow(ad_img)
    plt.imshow(heatmap_resized, cmap="jet", alpha=0.5)
    plt.colorbar(label="Gaze Fixation Intensity")
    plt.title("Gaze Heatmap")
    plt.axis('off')
    plt.show()

def main(ad_path):
    gaze_tracking = GazeTracking()
    screen_width, screen_height = get_screen_resolution()
    transformation_matrix, avg_distance = calibrate_gaze(gaze_tracking, screen_width, screen_height)
    heatmap = show_ad(ad_path, gaze_tracking, screen_width, screen_height, transformation_matrix, avg_distance)
    display_heatmap(heatmap, ad_path, screen_width, screen_height)

if __name__ == "__main__":
    image_path = os.path.join("data/PHOTO-2025-03-02-09-10-01.jpg")
    main(image_path)