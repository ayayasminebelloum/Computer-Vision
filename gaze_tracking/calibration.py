from __future__ import division
import cv2
import numpy as np
from .pupil import Pupil


class Calibration(object):
    """
    This class calibrates the pupil detection algorithm by finding the
    best binarization threshold value for the person and the webcam.
    """

    def __init__(self):
        self.nb_frames = 20  # Number of frames for calibration
        self.thresholds_left = []
        self.thresholds_right = []

    def is_complete(self):
        """Returns True if the calibration is completed."""
        return len(self.thresholds_left) >= self.nb_frames and len(self.thresholds_right) >= self.nb_frames

    def threshold(self, side):
        """Returns the final threshold value for the given eye.

        Argument:
            side: 0 for left eye, 1 for right eye
        """
        if side == 0 and self.thresholds_left:
            return int(np.percentile(self.thresholds_left, 50))  # Use percentile for stability
        elif side == 1 and self.thresholds_right:
            return int(np.percentile(self.thresholds_right, 50))
        return 0

    @staticmethod
    def preprocess_eye_frame(eye_frame):
        """Applies noise reduction and contrast improvement."""
        # Convert to grayscale (if not already)
        eye_frame = cv2.cvtColor(eye_frame, cv2.COLOR_BGR2GRAY) if len(eye_frame.shape) == 3 else eye_frame
        
        # Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        eye_frame = clahe.apply(eye_frame)

        # Reduce noise with bilateral filtering
        eye_frame = cv2.bilateralFilter(eye_frame, 10, 15, 15)
        
        return eye_frame

    @staticmethod
    def iris_size(frame):
        """Returns the percentage of space the iris occupies.

        Argument:
            frame (numpy.ndarray): Binarized iris frame
        """
        frame = frame[5:-5, 5:-5]  # Crop edges to avoid noise
        height, width = frame.shape[:2]
        nb_pixels = height * width
        nb_blacks = nb_pixels - cv2.countNonZero(frame)  # Count dark pixels
        return nb_blacks / nb_pixels

    @staticmethod
    def find_best_threshold(eye_frame):
        """Finds the optimal threshold for pupil detection.

        Argument:
            eye_frame (numpy.ndarray): Grayscale frame of the eye
        """
        eye_frame = Calibration.preprocess_eye_frame(eye_frame)  # Preprocess before thresholding
        average_iris_size = 0.48
        trials = {}

        for threshold in range(5, 100, 2):  # Smaller step size for precision
            iris_frame = Pupil.image_processing(eye_frame, threshold)
            trials[threshold] = Calibration.iris_size(iris_frame)

        best_threshold, _ = min(trials.items(), key=lambda p: abs(p[1] - average_iris_size))

        return best_threshold

    def evaluate(self, eye_frame, side):
        """Improves calibration by analyzing the given eye frame.

        Arguments:
            eye_frame (numpy.ndarray): Frame of the eye
            side: 0 for left eye, 1 for right eye
        """
        threshold = self.find_best_threshold(eye_frame)

        if side == 0:
            self.thresholds_left.append(threshold)
        elif side == 1:
            self.thresholds_right.append(threshold)