import cv2
import numpy as np
from screeninfo import get_monitors

WINDOW_NAME = "Gaze Tracker"

# Get primary screen resolution
def get_screen_resolution():
    monitor = get_monitors()[0]
    return monitor.width, monitor.height

# Initialize fullscreen window and force correct size
def init_fullscreen_window():
    screen_width, screen_height = get_screen_resolution()
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.resizeWindow(WINDOW_NAME, screen_width, screen_height)

# Draw centered multiline text
def draw_text_lines(canvas, lines, start_y, font_scale=1.2, color=(255,255,255), thickness=2, line_gap=40, center=True):
    y = start_y
    for line in lines:
        text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        x = (canvas.shape[1] - text_size[0]) // 2 if center else 100
        cv2.putText(canvas, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        y += line_gap

# Draw a list of buttons [(label, (x, y))]
def draw_buttons(canvas, buttons):
    for text, (x, y) in buttons:
        cv2.rectangle(canvas, (x, y), (x + 600, y + 100), (180, 60, 100), -1)
        cv2.putText(canvas, text, (x + 50, y + 65), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 3)

# Draw Exit and Home buttons
def draw_exit_and_home(canvas, screen_width, screen_height, show_home_button=False):
    # Exit button
    cv2.rectangle(canvas, (screen_width - 170, screen_height - 100), (screen_width - 20, screen_height - 20), (60, 60, 180), -1)
    cv2.putText(canvas, "Exit", (screen_width - 140, screen_height - 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    if show_home_button:
        # Home button (bottom left corner)
        cv2.rectangle(canvas, (20, screen_height - 100), (170, screen_height - 20), (60, 180, 60), -1)
        cv2.putText(canvas, "Home", (50, screen_height - 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

# Detect which button (index) was clicked, or return -1 (Exit), -2 (Home), or None
def detect_button_click(x, y, buttons, screen_width, screen_height, show_home_button=False):
    for i, (_, (bx, by)) in enumerate(buttons):
        if bx <= x <= bx + 600 and by <= y <= by + 100:
            return i

    # Exit button (bottom-right)
    if screen_width - 170 <= x <= screen_width - 20 and screen_height - 100 <= y <= screen_height - 20:
        return -1

    if show_home_button:
        # Home button (bottom-left)
        if 20 <= x <= 170 and screen_height - 100 <= y <= screen_height - 20:
            return -2

    return None

# Show menu screen

def show_menu_screen(screen_width, screen_height, title_lines, buttons, show_home_button=False):
    clicked = []
    result = [None]

    def click_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            idx = detect_button_click(x, y, buttons, screen_width, screen_height, show_home_button=show_home_button)
            result[0] = idx

    init_fullscreen_window()
    cv2.setMouseCallback(WINDOW_NAME, click_callback)

    while result[0] is None:
        canvas = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        canvas[:] = (20, 20, 20)
        draw_text_lines(canvas, title_lines, 100)
        draw_buttons(canvas, buttons)
        draw_exit_and_home(canvas, screen_width, screen_height, show_home_button=show_home_button)

        cv2.imshow(WINDOW_NAME, canvas)
        if cv2.waitKey(1) == 27:
            break

    return result[0]

# Show a fullscreen message until key press or exit click
def show_message_screen(screen_width, screen_height, message_lines, window_name="Gaze Tracker"):
    init_fullscreen_window()
    canvas = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
    draw_text_lines(canvas, message_lines, 200)
    draw_exit_and_home(canvas, screen_width, screen_height, show_home_button=False)

    clicked_exit = [False]

    def exit_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if detect_button_click(x, y, [], screen_width, screen_height, show_home_button=False) == -1:
                clicked_exit[0] = True

    cv2.setMouseCallback(window_name, exit_callback)

    while not clicked_exit[0]:
        cv2.imshow(window_name, canvas)
        if cv2.waitKey(1) == 27:
            break

    cv2.destroyWindow(window_name)