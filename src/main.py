# 1. Importing necessary libraries and modules:
import cv2
import numpy as np
from gaze_tracking import GazeTracking
from ad_tracking.calibrate import run_calibration
from ad_tracking.ad import choose_ad, show_ad, display_heatmap
from ad_tracking.camera import show_live_coordinates
from utils.ui_utils import get_screen_resolution, show_menu_screen, show_message_screen

def main():
    # 2.1 - Get screen resolution for fullscreen display
    screen_width, screen_height = get_screen_resolution()

    # 2.2 - Initialize the gaze tracking object and calibration variables
    gaze_tracking = GazeTracking()
    transformation_matrix = None
    avg_distance = None

    # 2.3 - Create a fullscreen window for consistent display
    cv2.namedWindow("Gaze Tracker", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Gaze Tracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # 3. Main application loop
    while True:
        # 3.1 - Determine if calibration has been completed
        calibrated = transformation_matrix is not None and avg_distance is not None

        # 3.2 - Title text for the main menu
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

        # 3.3 - Menu buttons: Only show all options after calibration
        if not calibrated:
            buttons = [("Calibrate Gaze", (550, 650))]
            enabled_flags = [True]
        else:
            buttons = [
                ("Calibrate Gaze", (200, 600)),
                ("Live Camera Mode", (900, 600)),
                ("Ad + Heatmap", (200, 750)),
            ]
            enabled_flags = [True, True, True]

        # 3.4 - Display the interactive menu screen and get user's choice
        choice = show_menu_screen(
            screen_width,
            screen_height,
            title,
            buttons,
            show_home_button=False,
            enabled=enabled_flags
        )

        # 4. Calibrate Gaze option
        if choice == 0:
            transformation_matrix, avg_distance, gaze_tracking = run_calibration(window_name="Gaze Tracker")

        # 5. Live Camera Mode
        elif choice == 1:
            result = show_live_coordinates(
                gaze_tracking,
                screen_width,
                screen_height,
                transformation_matrix,
                avg_distance,
                window_name="Gaze Tracker"
            )
            if result == -1:  # User exited
                break
            elif result == -2:  # User chose to return to menu
                continue

        # 6. Ad + Heatmap mode
        elif choice == 2:
            # 6.1 - Show ad selection screen
            ad_path = choose_ad(screen_width, screen_height, window_name="Gaze Tracker")

            # 6.2 - Handle user cancelling or exiting ad selection
            if ad_path is None:
                continue
            elif ad_path == -1:
                break
            elif ad_path == -2:
                continue

            # 6.3 - Show ad and collect gaze heatmap
            heatmap = show_ad(
                ad_path,
                gaze_tracking,
                screen_width,
                screen_height,
                transformation_matrix,
                avg_distance,
                window_name="Gaze Tracker"
            )

            # 6.4 - Handle interruptions during ad playback
            if isinstance(heatmap, int):
                if heatmap == -1:
                    break
                elif heatmap == -2:
                    continue
            else:
                # 6.5 - Display resulting heatmap on top of ad
                display_heatmap(heatmap, ad_path, screen_width, screen_height)

        # 7. Exit button clicked or menu closed
        elif choice == -1 or choice is None:
            print("Exit button clicked. Closing application...")
            break

    # 8. Clean up windows and resources
    cv2.destroyAllWindows()

# 9. Entry point
if __name__ == "__main__":
    main()
