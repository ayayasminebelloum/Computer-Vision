import cv2
import numpy as np
from gaze_tracking import GazeTracking
from ad_tracking.calibrate import run_calibration
from ad_tracking.ad import choose_ad, show_ad, display_heatmap
from ad_tracking.camera import show_live_coordinates
from utils.ui_utils import get_screen_resolution, show_menu_screen, show_message_screen

def main():
    screen_width, screen_height = get_screen_resolution()
    gaze_tracking = GazeTracking()
    transformation_matrix = None
    avg_distance = None

    # Create one persistent fullscreen OpenCV window
    cv2.namedWindow("Gaze Tracker", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Gaze Tracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        title = [
            "Welcome to the Gaze Tracker!",
            "",
            "This app uses computer vision to track where you're looking on the screen.",
            "You can use it to explore live gaze detection or analyze which parts of ads attract the most attention.",
            "",
            "Calibrate Gaze: Setup your eyes so tracking is accurate.",
            "Live Camera Mode: See real-time gaze tracking.",
            "Ad + Heatmap: Watch an ad and generate a gaze heatmap.",
            "",
            "Choose one of the options below to get started."
        ]

        buttons = [
            ("Calibrate Gaze", (200, 600)),
            ("Live Camera Mode", (900, 600)),
            ("Ad + Heatmap", (200, 750)),
        ]

        choice = show_menu_screen(screen_width, screen_height, title, buttons, show_home_button=False)

        if choice == 0:
            transformation_matrix, avg_distance, gaze_tracking = run_calibration(window_name="Gaze Tracker")

        elif choice == 1:
            if transformation_matrix is None or avg_distance is None:
                show_message_screen(screen_width, screen_height, [
                    "Please calibrate before using camera mode.",
                    "Press any key to return to menu."
                ], window_name="Gaze Tracker", show_home_button=True)
            else:
                result = show_live_coordinates(gaze_tracking, screen_width, screen_height, transformation_matrix, avg_distance, window_name="Gaze Tracker")
                if result == -1:
                    break  # Exit
                elif result == -2:
                    continue  # Go Home (menu)

        elif choice == 2:
            if transformation_matrix is None or avg_distance is None:
                show_message_screen(screen_width, screen_height, [
                    "Please calibrate before viewing ads.",
                    "Press any key to return to menu."
                ], window_name="Gaze Tracker", show_home_button=True)
            else:
                ad_path = choose_ad(screen_width, screen_height, window_name="Gaze Tracker")
                if ad_path == -1:
                    break
                elif ad_path == -2:
                    continue

                heatmap = show_ad(ad_path, gaze_tracking, screen_width, screen_height, transformation_matrix, avg_distance, window_name="Gaze Tracker")
                if isinstance(heatmap, int):  # Exit or Home clicked mid-ad
                    if heatmap == -1:
                        break
                    elif heatmap == -2:
                        continue
                else:
                    display_heatmap(heatmap, ad_path, screen_width, screen_height)

        elif choice == -1 or choice is None:
            print("Exit button clicked. Closing application...")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()