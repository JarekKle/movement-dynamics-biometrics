import math
from uuid import uuid4
import time

from PyQt6.QtCore import QTimer, QObject, pyqtSignal

from application.app_config import RecordingConfig
from domain.recording.recording_state import RecordingState
from domain.recording.skeleton_image_recording import SkeletonImageRecording
from domain.recording.skeleton_recording import SkeletonRecording


class RecordingController(QObject):
    recording_finished = pyqtSignal(object, object)

    def __init__(self, source_controller, repository, parent=None):
        super().__init__(parent)
        self.still_frames = 0
        self.still_anchor = None
        self.remaining_seconds = 0
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.state_reset_timer = QTimer(self)
        self.timer.timeout.connect(self.on_second_passed)
        self.state_reset_timer.timeout.connect(self.on_state_reset)
        self.source_controller = source_controller
        self.repository = repository
        self.state = RecordingState.NOT_RECORDING
        self.recording = None
        self.skeleton_image_recording = None
        self.next_sample_time = None
        self.start_time = None
        self.current_still_movement_duration = 0.0
        self.still_movement_start_time = None
        self.last_movement_time = None
        self.last_missing_time = None
        self.configure(RecordingConfig())

        self.sample_rate: float
        self.countdown_seconds: int
        self.movement_activity_detection: bool
        self.still_movement_duration_threshold: float
        self.joint_movement_threshold: float
        self.active_joint_ratio_threshold: float
        self.min_frames: float
        self.max_missing_seconds: float
    def configure(self, cfg: RecordingConfig):
        self.sample_rate = cfg.sample_rate
        self.countdown_seconds = cfg.countdown_seconds
        self.movement_activity_detection = cfg.movement_activity_detection
        self.still_movement_duration_threshold = cfg.still_movement_duration_threshold
        self.joint_movement_threshold = cfg.joint_movement_threshold
        self.active_joint_ratio_threshold = cfg.active_joint_ratio_threshold
        self.max_missing_seconds = cfg.max_missing_seconds
        self.min_frames = max(1, round(cfg.min_recording_seconds * cfg.sample_rate))
        self.state_reset_timer.setInterval(int(cfg.result_display_seconds * 1000))
    def is_recording(self):
        return self.state == RecordingState.RECORDING

    def start_recording(self, metadata=None):
        if self.is_recording():
            return
        recording_id = uuid4()
        self.recording = SkeletonRecording(
            recording_id=str(recording_id),
            sample_rate=self.sample_rate,
            frames=[],
            metadata=metadata or {}
        )
        self.skeleton_image_recording = SkeletonImageRecording(
            recording_id=str(recording_id) + "image",
            sample_rate=self.sample_rate,
            frames=[],
            metadata=metadata or {}
        )
        self.change_state(RecordingState.COUNTING_DOWN)
        self.last_missing_time = None
        self.start_time = time.time()
        self.next_sample_time = 0
        self.remaining_seconds = self.countdown_seconds
        self.state_reset_timer.stop()
        self.still_anchor = None
        self.still_frames = 0
        self.timer.start()


    def add_frames(self, frame, joints_2d):
        if not self.is_recording():
            return
        if frame is None or joints_2d is None:
            self.handle_missing_frame()
            return
        self.last_missing_time = None
        # if self.movement_activity_detection:
        #     self.determine_still_movement(frame)
        if not self.is_frame_time_valid():
            return
        time_diff = time.time() - self.start_time
        self.next_sample_time = time_diff + ( 1.0 / self.sample_rate)

        self.add_frame(frame)
        self.add_image_frame(joints_2d)
        if self.movement_activity_detection:
            self.update_stillness(frame)
            still_frames_limit = round(self.still_movement_duration_threshold*self.sample_rate)
            if self.still_frames >= still_frames_limit:
                self.handle_still_movement()
    def handle_missing_frame(self):
        curr_time = time.time()
        if self.last_missing_time is None:
            self.last_missing_time = curr_time
        if curr_time - self.last_missing_time >= self.max_missing_seconds:
            self.cancel_recording()
    def update_stillness(self,frame):
        if self.still_anchor is None:
            self.still_anchor = frame
            self.still_frames = 0
            return
        joint_activity = self.calculate_joint_activity(self.still_anchor, frame)
        if joint_activity >= self.active_joint_ratio_threshold:
            self.still_anchor = frame
            self.still_frames = 0
        else:
            self.still_frames += 1
    def is_frame_time_valid(self):
        current_time = time.time() - self.start_time
        if self.next_sample_time == 0:
            return True
        return self.next_sample_time < current_time
    def get_last_frame(self):
        if not self.is_recording_empty():
            return self.recording.frames[-1]
        return None
    def determine_still_movement(self, frame):
        old_frame = self.get_last_frame()
        if old_frame is None:
            self.handle_changing_frame()
            return
        active_ratio = self.calculate_joint_activity(old_frame, frame)

        if active_ratio >= self.active_joint_ratio_threshold:
            # print(f"[CHANGING FRAME] Active ratio: {active_ratio}, still duration: {self.current_still_movement_duration}")

            self.handle_changing_frame()
        else:
            # print(f"[STILL FRAME] Active ratio: {active_ratio}, still duration: {self.current_still_movement_duration}")

            self.handle_still_frame()
    def calculate_joint_activity(self, old_frame, frame):
        joint_count = 0
        active_joints = 0
        for joint_name, new_joint in frame.joints.items():
            prev_joint = old_frame.joints.get(joint_name)
            if prev_joint is None:
                continue
            joint_count += 1
            dist = self.calculate_joint_distance(prev_joint, new_joint)
            if dist > self.joint_movement_threshold:
                active_joints += 1
        if joint_count == 0:
            return 1
        return active_joints / joint_count

    def handle_still_frame(self):
        current_time = time.time()
        if self.still_movement_start_time is None:
            self.still_movement_start_time = current_time
        self.current_still_movement_duration = current_time - self.still_movement_start_time
    def is_still_movement(self):
        return self.current_still_movement_duration >= self.still_movement_duration_threshold
    def handle_changing_frame(self):
        self.still_movement_start_time = None
        self.current_still_movement_duration = 0
        self.last_movement_time = time.time()
    def handle_still_movement(self):

        still_frame_count = self.still_frames
        if still_frame_count > 0:
            del self.recording.frames[-still_frame_count:]
        if len(self.skeleton_image_recording.frames)>0:
            del self.skeleton_image_recording.frames[-still_frame_count:]
        if len(self.recording.frames) < self.min_frames:
            self.cancel_recording()
        else:
            self.stop_recording()
    def is_recording_empty(self):
        if self.recording is None:
            return True
        return len(self.recording.frames) == 0
    def add_frame(self, frame):
        self.recording.frames.append(frame)

    def add_image_frame(self, joints_2d):
        self.skeleton_image_recording.frames.append(joints_2d)

    def change_state(self, new_state):
        self.state = new_state
        self.source_controller.recording_state = self.state
        self.source_controller.remaining_seconds = self.remaining_seconds

    def stop_recording(self):
        self.timer.stop()
        if self.state == RecordingState.COUNTING_DOWN:
            self.cancel_recording()
            return None
        if not self.is_recording():
            return None
        self.change_state(RecordingState.FINISHED_RECORDING)
        self.state_reset_timer.start()
        recording = self.recording
        skeleton_image_recording = self.skeleton_image_recording
        self.recording = None
        self.skeleton_image_recording = None
        self.next_sample_time = None
        self.start_time = None
        self.recording_finished.emit(recording, skeleton_image_recording)
        return recording, skeleton_image_recording

    def save_recording(self, recording):
        self.repository.save(recording)

    def save_image_recording(self, image_recording):
        self.repository.save(image_recording)

    def cancel_recording(self):
        self.timer.stop()
        self.change_state(RecordingState.CANCELLED_RECORDING)
        self.state_reset_timer.start()

    def on_second_passed(self):

        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            self.change_state(RecordingState.COUNTING_DOWN)
            return
        else:
            if not self.source_controller.is_ready_to_record():
                self.timer.stop()
                self.change_state(RecordingState.CANCELLED_RECORDING)
                self.state_reset_timer.start()
                return
        self.timer.stop()
        self.change_state(RecordingState.RECORDING)

    def on_state_reset(self):
        self.change_state(RecordingState.NOT_RECORDING)
        self.state_reset_timer.stop()

    def get_recording_status(self):
        return self.state

    def get_recording_countdown_seconds(self):
        return self.remaining_seconds

    def calculate_joint_distance(self, prev_joint, curr_joint):
        dx = curr_joint.x - prev_joint.x
        dy = curr_joint.y - prev_joint.y
        dz = curr_joint.z - prev_joint.z
        return math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
