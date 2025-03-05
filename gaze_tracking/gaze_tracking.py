from __future__ import division
import math
import os
import cv2
import dlib
from .eye import Eye
from .calibration import Calibration

class GazeTracking:
    """Tracks the user's gaze direction based on detected pupils and blinks."""

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()

        # Load face detector and landmark predictor
        self._face_detector = dlib.get_frontal_face_detector()
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat")
        self._predictor = dlib.shape_predictor(model_path)

    @property
    def pupils_located(self):
        """Checks if the pupils have been successfully located"""
        return all([
            self.eye_left and self.eye_left.pupil and self.eye_left.pupil.x is not None,
            self.eye_right and self.eye_right.pupil and self.eye_right.pupil.x is not None
        ])

    def _analyze(self):
        """Detects face and extracts eye landmarks."""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        if len(faces) == 0:
            self.eye_left, self.eye_right = None, None
            return

        landmarks = self._predictor(frame, faces[0])
        self.eye_left = Eye(frame, landmarks, 0, self.calibration)
        self.eye_right = Eye(frame, landmarks, 1, self.calibration)

    def refresh(self, frame):
        """Refreshes frame and analyzes it."""
        self.frame = frame
        self._analyze()

    def pupil_left_coords(self):
        """Returns left pupil coordinates (x, y)"""
        return (
            self.eye_left.origin[0] + self.eye_left.pupil.x,
            self.eye_left.origin[1] + self.eye_left.pupil.y
        ) if self.pupils_located else None

    def pupil_right_coords(self):
        """Returns right pupil coordinates (x, y)"""
        return (
            self.eye_right.origin[0] + self.eye_right.pupil.x,
            self.eye_right.origin[1] + self.eye_right.pupil.y
        ) if self.pupils_located else None

    def horizontal_ratio(self):
        """Returns a number between 0.0 (right) and 1.0 (left) for horizontal gaze direction."""
        if not self.pupils_located:
            return 0.5

        left_ratio = self.eye_left.pupil.x / (self.eye_left.center[0] * 2 - 10)
        right_ratio = self.eye_right.pupil.x / (self.eye_right.center[0] * 2 - 10)

        return (left_ratio + right_ratio) / 2

    def vertical_ratio(self):
        """Returns a number between 0.0 (up) and 1.0 (down) for vertical gaze direction."""
        if not self.pupils_located:
            return 0.5

        left_eye_height = abs(self.eye_left.landmark_points[5][1] - self.eye_left.landmark_points[1][1])
        right_eye_height = abs(self.eye_right.landmark_points[5][1] - self.eye_right.landmark_points[1][1])

        if left_eye_height == 0 or right_eye_height == 0:
            return 0.5  # Prevents division by zero

        left_ratio = (self.eye_left.pupil.y - self.eye_left.origin[1]) / max(1, left_eye_height)
        right_ratio = (self.eye_right.pupil.y - self.eye_right.origin[1]) / max(1, right_eye_height)

        avg_ratio = (left_ratio + right_ratio) / 2

        return min(max(avg_ratio * 1.2, 0.0), 1.0)  # Scaled for sensitivity

    def is_left(self):
        """Returns True if the user is looking LEFT"""
        return self.pupils_located and self.horizontal_ratio() > 0.65

    def is_right(self):
        """Returns True if the user is looking RIGHT"""
        return self.pupils_located and self.horizontal_ratio() < 0.35

    def is_up(self):
        """Returns True if the user is looking UP"""
        return self.pupils_located and self.vertical_ratio() < 0.35

    def is_down(self):
        """Returns True if the user is looking DOWN"""
        return self.pupils_located and self.vertical_ratio() >= 0.6

    def is_center_horizontal(self):
        """Returns True if the user is looking CENTER horizontally."""
        return 0.4 <= self.horizontal_ratio() <= 0.6  # Adjusted for better accuracy

    def is_center_vertical(self):
        """Returns True if the user is looking CENTER vertically."""
        return 0.4 <= self.vertical_ratio() <= 0.6  # Adjusted for normal variance

    def is_strong_left(self):
        """Returns True if the user is looking strongly to the left"""
        return self.pupils_located and self.horizontal_ratio() > 0.75

    def is_strong_right(self):
        """Returns True if the user is looking strongly to the right"""
        return self.pupils_located and self.horizontal_ratio() < 0.25

    def eye_aspect_ratio(self, eye):
        """Computes the eye aspect ratio (EAR) to detect blinking."""
        vertical1 = math.dist(eye.landmark_points[1], eye.landmark_points[5])
        vertical2 = math.dist(eye.landmark_points[2], eye.landmark_points[4])
        horizontal = math.dist(eye.landmark_points[0], eye.landmark_points[3])

        if horizontal == 0:
            return 1  # Avoid division by zero

        return (vertical1 + vertical2) / (2.0 * horizontal)

    def is_blinking(self):
        """Returns True if the user is blinking based on the EAR threshold."""
        if not self.pupils_located:
            return False

        ear_left = self.eye_aspect_ratio(self.eye_left)
        ear_right = self.eye_aspect_ratio(self.eye_right)
        ear_avg = (ear_left + ear_right) / 2

        if self.is_down():
            blink_threshold = 0.16  # Lower threshold when looking down
        else:
            blink_threshold = 0.22  # Default

        return ear_avg < blink_threshold

    def annotated_frame(self):
        """Draws pupil tracking points on the frame."""
        frame = self.frame.copy()
        if self.pupils_located:
            color = (0, 255, 0)
            cv2.circle(frame, self.pupil_left_coords(), 3, color, -1)
            cv2.circle(frame, self.pupil_right_coords(), 3, color, -1)
        return frame