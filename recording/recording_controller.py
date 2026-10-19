from uuid import uuid4
import time
from recording.skeleton_recording import SkeletonRecording


class RecordingController:
    def __init__(self, repository, sample_rate):
        self.repository = repository
        self.sample_rate = sample_rate
        self.recording = None
        self.next_sample_time = None
        self.start_time = None
    def is_recording(self):
        return self.recording is not None
    def start_recording(self, metadata=None):
        if self.is_recording():
            return
        self.recording = SkeletonRecording(
            recording_id=str(uuid4()),
            sample_rate=self.sample_rate,
            frames=[],
            metadata=metadata or {}
        )
        self.start_time = time.time()

        self.next_sample_time = 0
    def add_frame(self, frame):
        if not self.is_recording():
            return
        time_diff = time.time() - self.start_time
        self.recording.frames.append(frame)
        self.next_sample_time = time_diff + 1/self.sample_rate

    def stop_recording(self):
        if not self.is_recording():
            return None
        recording = self.recording
        self.recording = None
        self.next_sample_time = None
        self.start_time = None
        return recording
    def save_recording(self, recording):
        self.repository.save(recording)