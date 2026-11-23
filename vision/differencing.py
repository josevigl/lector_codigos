import cv2
import numpy as np


class FrameDifferencer:
    def __init__(self, mean_difference_threshold):
        if mean_difference_threshold < 0:
            raise ValueError("El umbral de diferencia no puede ser negativo.")
        self.threshold = float(mean_difference_threshold)
        self._previous = None

    def changed(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self._previous is None or self._previous.shape != gray.shape:
            self._previous = gray
            return True

        difference = cv2.absdiff(gray, self._previous)
        self._previous = gray
        return float(np.mean(difference)) >= self.threshold
