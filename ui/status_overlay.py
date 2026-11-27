from enum import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from domain.recording.recording_state import RecordingState
from sources.tracking_status import TrackingStatus


class Position(Enum):
    TOP_LEFT = "Top left",
    CENTER = "Center",
    BOTTOM = "Bottom left",
class LabelColor(Enum):
    GREEN = "#4bae49"
    YELLOW = "#feb200"
    RED = "#e43834"

class StatusOverlay(QLabel):
    def __init__(self, camera_label):
        super().__init__(camera_label)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._last_params = None
        self.hide()

    def show_status(self, source_status, recording_status, remaining_seconds):
        messages = {
            TrackingStatus.SOURCE_DISCONNECTED: ("Camera disconnected", LabelColor.RED),
            TrackingStatus.SOURCE_PAUSED: ("Camera paused", LabelColor.YELLOW),
            TrackingStatus.NO_PEOPLE_TRACKED: ("Step into the frame", LabelColor.YELLOW),
            TrackingStatus.PERSON_LOST: ("Step back into the frame", LabelColor.YELLOW),
            TrackingStatus.TOO_MANY_PEOPLE_TRACKED: ("One person allowed", LabelColor.YELLOW),
            TrackingStatus.REQUIRED_JOINTS_NOT_TRACKED: ("Not all joints visible", LabelColor.YELLOW),
            TrackingStatus.ERROR: ("Unknown error", LabelColor.RED),
        }
        if recording_status == RecordingState.COUNTING_DOWN:
            self.display_text(str(max(remaining_seconds, 0)), LabelColor.YELLOW, Position.CENTER, 0.45)
        elif recording_status == RecordingState.RECORDING:
            self.display_text("● REC", LabelColor.RED, Position.TOP_LEFT, 0.09)
        elif recording_status == RecordingState.FINISHED_RECORDING:
            self.display_text("Recording done", LabelColor.GREEN, Position.CENTER, 0.12)
        elif recording_status == RecordingState.CANCELLED_RECORDING:
            self.display_text("Recording cancelled", LabelColor.RED, Position.CENTER, 0.12)
        elif source_status in messages:
            text, color = messages[source_status]
            self.display_text(text, color, Position.BOTTOM, 0.08)
        else:
            self.hide_text()

    def is_params_changed(self, text, color, position, size):
        return [text, color, position, size] == self._last_params

    def display_text(self, text, color, position, size):
        parent = self.parentWidget()
        if self.is_params_changed(text, color, position, size):
            return
        self._last_params =[text, color, position, size]
        font_px = max(14, int(parent.height() * size))
        html = f"<div style='font-size:{font_px}px; font-weight:bold; color:{color.value}'>{text}</div>"
        self.setText(html)
        padding = max(6, font_px // 6)
        self.setStyleSheet(f"background: rgba(0, 0, 0, 150); border-radius: {padding}px; padding: {padding}px;")
        self.adjustSize()
        margin = max(8, parent.height() // 40)
        if position == Position.CENTER:
            x = (parent.width() - self.width()) // 2
            y = (parent.height() - self.height()) // 2
        elif position == Position.TOP_LEFT:
            x, y = margin, margin
        else:
            x = (parent.width() - self.width()) // 2
            y = parent.height() - self.height() - margin
        self.move(max(0, x), max(0, y))
        self.raise_()
        self.show()

    def hide_text(self):
        if self._last_params is not None:
            self._last_params = None
            self.hide()
