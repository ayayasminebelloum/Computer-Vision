import cv2
import numpy as np
import os

AD_PATH = os.path.abspath(os.path.join("..", "data", "ad5.jpg"))  # Change this if you want
WINDOW_NAME = "Heatmap Test"
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080  # Match your actual screen resolution

def resize_to_fullscreen(img, width, height):
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)

def generate_fake_heatmap(width, height):
    heatmap = np.zeros((height, width), dtype=np.float32)

    # Simulate some gaze points
    gaze_points = [
        (int(width * 0.3), int(height * 0.3)),
        (int(width * 0.5), int(height * 0.5)),
        (int(width * 0.7), int(height * 0.6)),
    ]

    for (x, y) in gaze_points:
        cv2.circle(heatmap, (x, y), 60, 1, -1)

    # Apply blur
    return cv2.GaussianBlur(heatmap, (101, 101), 0)

def show_heatmap(ad_img_path, heatmap):
    ad_img = cv2.imread(ad_img_path)
    if ad_img is None:
        print(f"❌ Failed to load ad image at {ad_img_path}")
        return

    ad_img = resize_to_fullscreen(ad_img, SCREEN_WIDTH, SCREEN_HEIGHT)
    heatmap = cv2.resize(heatmap, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Normalize and apply colormap
    heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_colored = cv2.applyColorMap(heatmap_normalized.astype(np.uint8), cv2.COLORMAP_JET)

    # Overlay heatmap onto ad image
    blended = cv2.addWeighted(ad_img, 0.5, heatmap_colored, 0.5, 0)

    while True:
        cv2.imshow(WINDOW_NAME, blended)
        if cv2.waitKey(1) == 27:  # ESC to exit
            break

    cv2.destroyWindow(WINDOW_NAME)

if __name__ == "__main__":
    heatmap = generate_fake_heatmap(SCREEN_WIDTH, SCREEN_HEIGHT)
    show_heatmap(AD_PATH, heatmap)