import numpy as np
import cv2


class Pupil(object):
    """
    This class detects the iris of an eye and estimates
    the position of the pupil
    """

    def __init__(self, eye_frame, threshold):
        self.iris_frame = None
        self.threshold = threshold
        self.x = None
        self.y = None

        self.detect_iris(eye_frame)

    @staticmethod
    def image_processing(eye_frame, threshold):
        """Performs operations on the eye frame to isolate the iris.

        Arguments:
            eye_frame (numpy.ndarray): Frame containing an eye and nothing else
            threshold (int): Threshold value used to binarize the eye frame

        Returns:
            A frame with a single element representing the iris
        """
        # Convert to grayscale (if not already)
        if len(eye_frame.shape) == 3:
            eye_frame = cv2.cvtColor(eye_frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to remove noise
        blurred_frame = cv2.GaussianBlur(eye_frame, (5, 5), 0)

        # Adaptive thresholding to improve robustness
        adaptive_threshold = cv2.adaptiveThreshold(
            blurred_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Apply morphological operations to clean the noise
        kernel = np.ones((3, 3), np.uint8)
        processed_frame = cv2.morphologyEx(adaptive_threshold, cv2.MORPH_OPEN, kernel)

        return processed_frame

    def detect_iris(self, eye_frame):
        """Detects the iris and estimates the position of the pupil by
        calculating the centroid.

        Arguments:
            eye_frame (numpy.ndarray): Frame containing an eye and nothing else
        """
        self.iris_frame = self.image_processing(eye_frame, self.threshold)

        # Try HoughCircles first (best for circular pupils)
        circles = cv2.HoughCircles(
            self.iris_frame, cv2.HOUGH_GRADIENT, dp=1.2, minDist=10,
            param1=50, param2=30, minRadius=5, maxRadius=30
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))
            self.x, self.y, _ = circles[0][0]  # Take first detected circle
            return

        # If HoughCircles fails, fallback to contour-based method
        contours, _ = cv2.findContours(self.iris_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for contour in contours:
            moments = cv2.moments(contour)
            if moments['m00'] != 0:
                self.x = int(moments['m10'] / moments['m00'])
                self.y = int(moments['m01'] / moments['m00'])
                return