import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel


class CameraLabel(QLabel):
    def __init__(self):
        super().__init__()
        self._last_image = None

    def refresh_frame(self, frame):
        self.update_frame(frame)

    def set_frame(self, frame: np.ndarray):
        self.update_frame(frame)
    def update_frame(self, original: np.ndarray):
        self._last_image = original
        self._set_label_image(original)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._last_image is not None:
            self._set_label_image(self._last_image)

    def get_target_size(self):
        ratio = self.devicePixelRatioF()
        width = max(16, int(self.width() * ratio))
        height = max(9, int(self.height() * ratio))
        aspect_w, aspect_h = [16, 9]
        if width * aspect_h > height * aspect_w:
            width = height * aspect_w // aspect_h
        else:
            height = width * aspect_h // aspect_w
        return min(width, 1920), min(height, 1080)
    def _set_label_image(self, image: np.ndarray):
        image = np.ascontiguousarray(image)
        h, w = image.shape[:2]
        if image.ndim == 3 and image.shape[2] == 4:
            image_format = QImage.Format.Format_RGB32
        else:
            image_format = QImage.Format.Format_BGR888
        qimg = QImage(image.data, w, h, image.strides[0], image_format)
        pixmap = QPixmap.fromImage(qimg)
        ratio = self.devicePixelRatioF()
        target_w, target_h = int(self.width() * ratio), int(self.height() * ratio)
        if w != target_w or h != target_h:
            pixmap = pixmap.scaled(target_w, target_h, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.FastTransformation)
        pixmap.setDevicePixelRatio(ratio)
        self.setPixmap(pixmap)
