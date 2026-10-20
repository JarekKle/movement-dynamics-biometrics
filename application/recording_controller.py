from uuid import uuid4
import time

from PyQt6.QtCore import QTimer, QObject

from domain.recording.recording_state import RecordingState
from domain.recording.skeleton_recording import SkeletonRecording


class RecordingController(QObject):
    def __init__(self, source_controller, repository, sample_rate, parent=None):
        super().__init__(parent)
        self.remaining_seconds = 0
        self.timer = QTimer(self)
        self.state_reset_timer = QTimer(self)
        self.timer.setInterval(1000)
        self.state_reset_timer.setInterval(5000)
        self.timer.timeout.connect(self.on_second_passed)
        self.state_reset_timer.timeout.connect(self.on_state_reset)
        self.source_controller = source_controller
        self.state = RecordingState.NOT_RECORDING
        self.repository = repository
        self.sample_rate = sample_rate
        self.countdown_seconds = 3
        self.recording = None
        self.next_sample_time = None
        self.start_time = None
    def is_recording(self):
        return self.state == RecordingState.RECORDING
    def start_recording(self, metadata=None):
        if self.is_recording():
            return
        if not self.source_controller.is_ready_to_record():
            return
        self.recording = SkeletonRecording(
            recording_id=str(uuid4()),
            sample_rate=self.sample_rate,
            frames=[],
            metadata=metadata or {}
        )
        self.change_state(RecordingState.COUNTING_DOWN)
        self.start_time = time.time()
        self.next_sample_time = 0
        self.remaining_seconds = self.countdown_seconds
        self.timer.start()
    def add_frame(self, frame):
        if not self.is_recording():
            return
        time_diff = time.time() - self.start_time
        self.recording.frames.append(frame)
        self.next_sample_time = time_diff + 1/self.sample_rate
    def change_state(self, new_state):
        self.state = new_state
        self.source_controller.recording_state = self.state
        self.source_controller.remaining_seconds = self.remaining_seconds
    def stop_recording(self):
        self.timer.stop()
        if not self.is_recording():
            return None
        self.change_state(RecordingState.FINISHED_RECORDING)
        self.state_reset_timer.start()
        recording = self.recording
        self.recording = None
        self.next_sample_time = None
        self.start_time = None
        return recording
    def save_recording(self, recording):
        self.repository.save(recording)
    def cancel_recording(self):
        self.timer.stop()
        self.change_state(RecordingState.CANCELLED_RECORDING)
        self.state_reset_timer.start()
    def on_second_passed(self):
        if not self.source_controller.is_ready_to_record():
            self.timer.stop()
            self.change_state(RecordingState.CANCELLED_RECORDING)
            self.state_reset_timer.start()
            return
        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            self.change_state(RecordingState.COUNTING_DOWN)
            return
        self.change_state(RecordingState.RECORDING)
    def on_state_reset(self):
        self.change_state(RecordingState.NOT_RECORDING)
        self.state_reset_timer.stop()
    def get_recording_status(self):
        return self.state
    def get_recording_countdown_seconds(self):
        return self.remaining_seconds
