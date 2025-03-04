import numpy as np
from gaze_tracking import GazeTracking
import time
import cv2
import matplotlib.pyplot as plt

def create_heatmap(ad_size):
    return np.zeros((ad_size[0], ad_size[1]))

def map_gaze_to_grid(gaze_x, gaze_y, webcam_size, ad_size):
    # Flip Y-axis (since webcam Y=0 is top, but OpenCV images Y=0 is bottom)
    flipped_gaze_y = webcam_size[1] - gaze_y  

    # Scale properly to ad size
    ad_x = int((gaze_x / webcam_size[0]) * ad_size[1])
    ad_y = int((flipped_gaze_y / webcam_size[1]) * ad_size[0])  # Correct Y scaling

    return ad_x, ad_y

def update_heatmap(heatmap, gaze_x, gaze_y, webcam_size, ad_size):
    if gaze_x is not None and gaze_y is not None:
        ad_x, ad_y = map_gaze_to_grid(gaze_x, gaze_y, webcam_size, ad_size)
        # Ensure integer indices within bounds:
        ad_x_int = min(int(ad_x), ad_size[1] - 1)
        ad_y_int = min(int(ad_y), ad_size[0] - 1)
        # Draw a small circle of radius 10 on the heatmap (to avoid the point getting drowned out)
        cv2.circle(heatmap, (ad_x_int, ad_y_int), 10, 1, -1)
        print(f"Gaze point (Webcam): ({gaze_x}, {gaze_y}) -> Mapped to Ad: ({ad_x}, {ad_y})")
        return heatmap

def show_ad(ad_path, gaze_tracking):
    frame = cv2.imread(ad_path)
    heatmap = create_heatmap(frame.shape)
    ad_height, ad_width, _ = frame.shape
    print("ad size", ad_height, ad_width)
    webcam = cv2.VideoCapture(0)
    webcam_width = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
    webcam_height = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    webcam_size = (webcam_width, webcam_height)
    print("webcam size", webcam_size)
    ad_size = (ad_height, ad_width)

    start_time = time.time()

    while time.time() - start_time < 10:
        ret, webcam_frame = webcam.read()
        gaze_tracking.refresh(webcam_frame) #allows us to loop through all gazed points with each frame... speed depends on the frame rate of each webcam
        left_pupil = gaze_tracking.pupil_left_coords()
        right_pupil = gaze_tracking.pupil_right_coords()

        if left_pupil:
            heatmap = update_heatmap(heatmap, left_pupil[0], left_pupil[1], webcam_size, ad_size)
        if right_pupil:
            heatmap = update_heatmap(heatmap, right_pupil[0], right_pupil[1], webcam_size, ad_size)

        cv2.namedWindow("Ad Display", cv2.WINDOW_NORMAL)  # Allow window resizing
        cv2.imshow("Ad Display", frame)

        # Center the window on the screen
        screen_width = 1920  # Adjust if needed
        screen_height = 1080  # Adjust if needed
        window_width = frame.shape[1]
        window_height = frame.shape[0]

        cv2.moveWindow("Ad Display", (screen_width - window_width) // 2, (screen_height - window_height) // 2)

        if cv2.waitKey(1) == 27:  
            break

    webcam.release()
    cv2.destroyAllWindows()
    return heatmap

def display_heatmap(heatmap, ad_path):
    img = cv2.imread(ad_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    smoothed_heatmap = cv2.GaussianBlur(heatmap, (31, 31), 0)
    plt.figure(figsize=(10, 6))
    plt.imshow(img)
    heatmap_display = plt.imshow(smoothed_heatmap, cmap="jet", alpha=0.5)
    plt.colorbar(heatmap_display, label="Gaze Fixation Intensity")
    plt.title("Gaze Heatmap")
    plt.show()

def main(ad_path):
    gaze = GazeTracking()
    print(f"Showing ad: {ad_path}")
    heatmap = show_ad(ad_path, gaze)
    display_heatmap(heatmap, ad_path)

if __name__ == "__main__":
    main('AdImages/PHOTO-2025-03-02-09-10-01.jpg')