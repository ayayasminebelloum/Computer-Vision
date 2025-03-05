import cv2
from gaze_tracking import GazeTracking

# Initialize gaze tracking
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

# Define the button position (bottom right)
button_text = "QUIT"
button_w, button_h = 100, 40  # Button width & height

def get_button_position(frame):
    """Dynamically calculate the button position based on the frame size."""
    height, width, _ = frame.shape
    return width - button_w - 30, height - button_h - 30  

def click_event(event, x, y, flags, param):
    """Detects when the quit button is clicked."""
    button_x, button_y = get_button_position(param)
    if event == cv2.EVENT_LBUTTONDOWN:
        if button_x <= x <= button_x + button_w and button_y <= y <= button_y + button_h:
            print("Quit button clicked. Exiting...")
            webcam.release()
            cv2.destroyAllWindows()
            exit(0)

cv2.namedWindow("Demo")

while True:
    ret, frame = webcam.read()

    if not ret or frame is None:
        print("Error: Could not capture frame from webcam.")
        continue

    # Ensure frame format is valid
    if len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    elif frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    # Process gaze tracking
    gaze.refresh(frame)
    frame = gaze.annotated_frame()

    # Get pupil coordinates
    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()

    # Debugging: Print raw gaze data
    horizontal_ratio = gaze.horizontal_ratio()
    vertical_ratio = gaze.vertical_ratio()
    print(f"Horizontal Ratio: {horizontal_ratio}, Vertical Ratio: {vertical_ratio}")

    gaze_direction = "Unknown"

    horizontal = gaze.horizontal_ratio()
    vertical = gaze.vertical_ratio()
    blinking = gaze.is_blinking()

    print(f"Horizontal Ratio: {horizontal}, Vertical Ratio: {vertical}, Blinking: {blinking}")

    if gaze.is_blinking():
        gaze_direction = "Blinking"
    elif gaze.is_strong_left() and gaze.is_up():
        gaze_direction = "Strong Left-Up"
    elif gaze.is_left() and gaze.is_up():
        gaze_direction = "Left-Up"
    elif gaze.is_strong_left():
        gaze_direction = "Strong Left"
    elif gaze.is_left():
        gaze_direction = "Left"
    elif gaze.is_strong_right() and gaze.is_up():
        gaze_direction = "Strong Right-Up"
    elif gaze.is_right() and gaze.is_up():
        gaze_direction = "Right-Up"
    elif gaze.is_strong_right():
        gaze_direction = "Strong Right"
    elif gaze.is_right():
        gaze_direction = "Right"
    elif gaze.is_center_horizontal() and gaze.is_up():
        gaze_direction = "Center-Up"
    elif gaze.is_center_horizontal() and gaze.is_down():
        gaze_direction = "Center-Down"
    else:
        gaze_direction = "Center-Center"
    # Debugging: Print out detected gaze direction
    print(f"Left Eye: {left_pupil} | Right Eye: {right_pupil} | Looking: {gaze_direction}")

    # Display gaze direction on screen
    cv2.putText(frame, f"Gaze: {gaze_direction}", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Display pupil coordinates
    cv2.putText(frame, f"Left Eye: {left_pupil}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"Right Eye: {right_pupil}", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Get button position dynamically
    button_x, button_y = get_button_position(frame)

    # Draw Quit Button
    cv2.rectangle(frame, (button_x, button_y), (button_x + button_w, button_y + button_h), (203, 192, 255), -1) 
    cv2.putText(frame, button_text, (button_x + 15, button_y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Set the mouse callback function for clicks
    cv2.setMouseCallback("Demo", click_event, param=frame)

    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == 27:
        break

webcam.release()
cv2.destroyAllWindows()