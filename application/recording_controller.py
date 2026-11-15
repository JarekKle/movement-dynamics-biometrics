import math
from uuid import uuid4
import time

from PyQt6.QtCore import QTimer, QObject, pyqtSignal

from domain.recording.recording_state import RecordingState
from domain.recording.skeleton_image_recording import SkeletonImageRecording
from domain.recording.skeleton_recording import SkeletonRecording


class RecordingController(QObject):
    recording_finished = pyqtSignal(object, object)
    def __init__(self, source_controller, repository, sample_rate, movement_activity_detection, parent=None):
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
        self.countdown_seconds = 5
        self.recording = None
        self.skeleton_image_recording = None
        self.next_sample_time = None
        self.start_time = None
        self.movement_activity_detection = True
        self.still_movement_duration_threshold = 2.0
        self.current_still_movement_duration = 0.0
        self.still_movement_start_time = None
        self.last_movement_time = None
        self.joint_movement_threshold = 0.1
        self.active_joint_ratio_threshold = 0.1

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
        self.start_time = time.time()
        self.next_sample_time = 0
        self.remaining_seconds = self.countdown_seconds
        self.timer.start()

    def add_frames(self, frame, joints_2d):
        if not self.is_recording():
            return
        if frame is None:
            self.cancel_recording()
        if self.movement_activity_detection:
            self.determine_still_movement(frame)
        if not self.is_frame_time_valid():
            return
        time_diff = time.time() - self.start_time
        self.next_sample_time = time_diff + ( 1.0 / self.sample_rate)

        self.add_frame(frame)
        self.add_image_frame(joints_2d)
        if self.movement_activity_detection and self.is_still_movement():
            self.handle_still_movement()
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
        for i, (joint_name, cords) in enumerate(frame.joints.items()):
            prev_joint = old_frame.joints[joint_name]
            new_joint = frame.joints[joint_name]
            dist = self.calculate_joint_distance(prev_joint,new_joint)
            joint_count += 1
            if dist > self.joint_movement_threshold:
                active_joints += 1
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
        # TODO: cut still frames
        still_frame_count = int(self.still_movement_duration_threshold*self.sample_rate - 1)
        del self.recording.frames[-still_frame_count:]
        if len(self.skeleton_image_recording.frames)>0:
            del self.skeleton_image_recording.frames[-still_frame_count:]
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
