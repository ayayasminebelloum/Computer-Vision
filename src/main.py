# 1. Importing necessary libraries and modules:
import cv2
import numpy as np
from gaze_tracking import GazeTracking
from ad_tracking.calibrate import run_calibration
from ad_tracking.ad import choose_ad, show_ad, display_heatmap
from ad_tracking.camera import show_live_coordinates
from utils.ui_utils import get_screen_resolution, show_menu_screen, show_message_screen

# --------------------------------------------------------------------------
# 2. The main function for running our Gaze Tracker app implementation: 
# --------------------------------------------------------------------------
def main():
    # 2.1 - Initializing Variables:
    screen_width, screen_height = get_screen_resolution()  # 2.1.1 - Getting screen resolution.
    gaze_tracking = GazeTracking()                         # 2.1.2 - Initializing gaze tracker.
    transformation_matrix = None                           # 2.1.3 - Placeholder for gaze calibration matrix.
    avg_distance = None                                    # 2.1.4 - Placeholder for user's average eye distance.

    # 2.2 - Creating a single fullscreen OpenCV window for the app:
    cv2.namedWindow("Gaze Tracker", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Gaze Tracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # 2.3 - Main loop to show the menu and respond to user input:
    while True:
        
        # 2.3.1 - Welcome screen title and instructions:
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

        # 2.3.2 - Buttons display positions on the menu screen:
        buttons = [
            ("Calibrate Gaze", (200, 600)),
            ("Live Camera Mode", (900, 600)),
            ("Ad + Heatmap", (200, 750)),
        ]

        # 2.3.3 - Showing menu and capturing user's selection:
        choice = show_menu_screen(screen_width, screen_height, title, buttons, show_home_button=False)

        # 2.3.4 - If the user selects "Calibrate Gaze":
        if choice == 0:
            transformation_matrix, avg_distance, gaze_tracking = run_calibration(window_name="Gaze Tracker")

        # 2.3.5 - If the user selects "Live Camera Mode":
        elif choice == 1:
            
            # Requirment --> calibration needs to be done before continuing:
            if transformation_matrix is None or avg_distance is None:
                show_message_screen(screen_width, screen_height, [
                    "Please calibrate before using camera mode.",
                    "Press any key to return to menu."
                ], window_name="Gaze Tracker", show_home_button=True)
            else:
                # Showing real-time gaze tracking feed:
                result = show_live_coordinates(gaze_tracking, screen_width, screen_height, transformation_matrix, avg_distance, window_name="Gaze Tracker")
                if result == -1:
                    break  # Exit
                elif result == -2:
                    continue  # Go Home (menu)

        # 2.3.6 - If user selects "Ad + Heatmap":
        elif choice == 2:

            # Requirment --> calibration needs to be done before continuing:
            if transformation_matrix is None or avg_distance is None:
                show_message_screen(screen_width, screen_height, [
                    "Please calibrate before viewing ads.",
                    "Press any key to return to menu."
                ], window_name="Gaze Tracker", show_home_button=True)
            else:
                # Letting the user choose an ad:
                ad_path = choose_ad(screen_width, screen_height, window_name="Gaze Tracker")
                if ad_path == -1:
                    break
                elif ad_path == -2:
                    continue

                # Showing the ad and collect gaze data to generate heatmap:
                heatmap = show_ad(ad_path, gaze_tracking, screen_width, screen_height, transformation_matrix, avg_distance, window_name="Gaze Tracker")

                # Checking if user exited mid-ad:
                if isinstance(heatmap, int):  
                    if heatmap == -1:
                        break
                    elif heatmap == -2:
                        continue
                else:
                    display_heatmap(heatmap, ad_path, screen_width, screen_height)

        # 2.3.7 - Handling exit button or ESC press from the menu:
        elif choice == -1 or choice is None:
            print("Exit button clicked. Closing application...")
            break

    # 2.3.8 - Cleaning up and closing all OpenCV windows:
    cv2.destroyAllWindows()

# 2.4 - Run main() to execute this file directly (the full program):
if __name__ == "__main__":
    main()
