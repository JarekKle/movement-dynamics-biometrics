import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel


class CameraLabel(QLabel):
    def __init__(self):
        super().__init__()

    def refresh_frame(self, frame):
        self.update_frame(frame)
    def set_frame(self, frame: np.ndarray):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        self.setPixmap(
            pixmap.scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
        )
    def update_frame(self, original: np.ndarray):
        self._set_label_image(original)
    def _set_label_image(self, image: np.ndarray):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(scaled_pixmap)
        return