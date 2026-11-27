from __future__ import annotations

import os
from datetime import datetime
from enum import Enum

from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout

from application.app_config import ConfigRepository, AppConfig
from application.movement_pattern_repository import MovementPatternRepository
from biometric.biometric_system import BiometricSystem
from domain.movement.kinect.kinect_skeleton_model import KinectSkeletonModel
from application.json_recording_repository import JsonRecordingRepository
from application.recording_controller import RecordingController
from domain.recording.movement_pattern import MovementPattern
from domain.recording.recording_state import RecordingState
from sources.kinect.kinect_skeleton_renderer import KinectSkeletonRenderer
from sources.kinect.kinect_source import KinectSource
from sources.source_controller import SourceController
from sources.source_registry import SourceRegistry
from ui.windows.classification_window import ClassificationWindow
from ui.kinect_joint_selection_dialog import KinectJointSelectionDialog
from ui.windows.config_window import ConfigWindow
from ui.windows.menu_window import MenuWindow
from ui.windows.movement_testing_window import MovementTestingWindow
from ui.windows.registration_window import RegistrationWindow


class AppStates(Enum):
    MENU = 0,
    REGISTRATION = 1,
    CLASSIFICATION = 2,
    TESTING = 3,
    CONFIG = 4


class AppManager(QWidget):
    def __init__(self, config_repository: ConfigRepository):
        """
        Initialize an AppManager object.
        """
        super().__init__()
        self.config_repository = config_repository
        self.config = config_repository.load()
        source = SourceRegistry[self.config.source_config.source]
        src_conf, rec_conf = self.config.source_config, self.config.recording_config
        if source == SourceRegistry.KINECT:
            self.skeleton_renderer = KinectSkeletonRenderer(src_conf.allow_inferred)
            self.source = KinectSource()
            self.skeleton_model = KinectSkeletonModel()
        self.joint_selection_map = self._get_joints_map_from_config()
        self._stored_joint_selection_map = None
        self.setWindowTitle("Movement dynamics biometrics")

        self.stack = QStackedWidget()

        self.biometric_system = BiometricSystem(self.skeleton_model, src_conf.allow_inferred)
        self.source_controller = SourceController(self.source, self.skeleton_renderer, src_conf.dynamic_tracking,
                                                  src_conf.allow_inferred, self.joint_selection_map)

        self.recording_repository = JsonRecordingRepository(rec_conf.directory)
        self.movement_pattern_repository = MovementPatternRepository(rec_conf.directory)
        self.recording_controller = RecordingController(self.source_controller, self.recording_repository)
        self.recording_controller.configure(rec_conf)

        self.recording_controller.recording_finished.connect(self.handle_recording_finish)
        self.menu_window = MenuWindow(self)
        self._app_state = AppStates.MENU
        self.movement_testing_window = None
        self.registration_window = None
        self.classification_window = None
        self.classification_results_page = None
        self.config_window = None

        self.stack.addWidget(self.menu_window)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def _is_recording_active(self):
        return self.get_recording_status() in (RecordingState.COUNTING_DOWN, RecordingState.RECORDING)
    def start_recording(self, metadata=None):
        """
        Activate a method in the recording controller to start recording.
        :return:
        """
        if self.recording_controller.is_recording():
            return
        self.recording_controller.start_recording(metadata)

    def stop_recording(self):
        """
        Activate a method in the recording controller to stop recording.
        :return: A dictionary of recorded joints and a dictionary of joints position on the screen.
        :rtype: dict
        """
        self.recording_controller.stop_recording()
    def handle_recording_finish(self, recording, skeleton_image_recording=None):
        if self._app_state == AppStates.REGISTRATION and self.registration_window is not None:
            self.registration_window.handle_recording_finish(recording, skeleton_image_recording)
            return
        self.save_recording(recording)
        if skeleton_image_recording is not None:
            self.save_recording(skeleton_image_recording)

    def save_recording(self, recording=None):
        """
        :param recording: A dictionary of recorded joints obtained from method AppManager.stop_recording() (could either be a recording or a skeleton image recording).
        :type recording: dict
        :return:
        """
        if recording is None:
            return
        self.recording_controller.save_recording(recording)

    def get_recording_status(self):
        """
        :return: attribute state of object self.recording_controller
        :rtype: RecordingState
        """
        return self.recording_controller.get_recording_status()

    def get_recording_countdown_seconds(self):
        """
        :return: attribute remaining_seconds of object self.recording_controller
        :rtype: int
        """
        return self.recording_controller.get_recording_countdown_seconds()

    def show_menu_window(self):
        """
        Sets currently displayed window to Menu and changed app's state to AppStates.MENU
        """
        if self._is_recording_active():
            self.recording_controller.cancel_recording()
        self.restore_joint_selection()
        self.source_controller.source.close()
        self.stack.setCurrentWidget(self.menu_window)
        self._app_state = AppStates.MENU

    def show_movement_testing_window(self):
        """
        Sets currently displayed window to Movement testing window and changed app's state to AppStates.TESTING
        """
        if self.movement_testing_window is None:
            self.movement_testing_window = MovementTestingWindow(self)
            self.stack.addWidget(self.movement_testing_window)
        self.stack.setCurrentWidget(self.movement_testing_window)
        self._app_state = AppStates.TESTING
        self.source_controller.source.open()

    def show_registration_window(self):
        """
        Sets currently displayed window to Registration window and changed app's state to AppStates.REGISTRATION
        """
        if self.registration_window is None:
            self.registration_window = RegistrationWindow(self)
            self.stack.addWidget(self.registration_window)
        if not self.registration_window.get_user_input():
            return
        self.stack.setCurrentWidget(self.registration_window)
        self._app_state = AppStates.REGISTRATION
        self.source_controller.source.open()
    def show_classification_window(self):
        """
        Sets currently displayed window to Classification window and changed app's state to AppStates.CLASSIFICATION
        """
        self.source_controller.source.close()
        if self.classification_window is None:
            self.classification_window = ClassificationWindow(self)
            self.stack.addWidget(self.classification_window)
        self.stack.setCurrentWidget(self.classification_window)
        self._app_state = AppStates.CLASSIFICATION

    def show_config_window(self):
        """
        Sets currently displayed window to Configuration window and changes app's state to AppStates.CONFIG
        """
        if self._is_recording_active():
            return
        self.source_controller.source.close()
        if self.config_window is None:
            self.config_window = ConfigWindow(self)
            self.config_window.load_values(self.config)
            self.stack.addWidget(self.config_window)
        self.stack.setCurrentWidget(self.config_window)
        self._app_state = AppStates.CONFIG
    def get_new_frame(self):
        """
        Receives new frame from a source controller and passes it to recording controller, if currently recording.
        :return: New color frame received from source controller.
        :rtype: ndarray
        """
        new_frame = self.source_controller.update_frame(self.config.source_config.dynamic_tracking)
        if self.recording_controller.is_recording():
            body = self.source_controller.get_joints_as_skeleton_frame()
            if not self.config.source_config.dynamic_tracking:
                self.source_controller.get_joints_data()
            joints_2d = self.source_controller.get_joints_2d_selected()
            self.recording_controller.add_frames(body, joints_2d)

        return new_frame

    def get_normalized_joints(self):
        """

        :return:
        """
        joints = self.source_controller.get_joints_raw()
        self.biometric_system.normalize_joints_by_shoulder_distance(joints)
        return self.biometric_system.get_joint_cords_normalized()

    def get_angles(self):
        joints = self.source_controller.get_joints_raw()
        self.biometric_system.calculate_angles(joints)
        return self.biometric_system.get_angles()

    def update_joints(self):
        self.source_controller.source.update_joint_cords()

    def get_joint_cords(self):
        return self.source_controller.source.get_joint_cords()

    def get_joint_selection_map(self):
        return self.joint_selection_map

    def stop_source(self):
        self.source_controller.source.stop()

    def start_source(self):
        self.source_controller.source.start()

    def open_source(self):
        self.source_controller.source.open()

    def close_source(self):
        self.source_controller.source.close()

    def get_tracking_status(self):
        self.source_controller.determine_tracking_status()
        return self.source_controller.get_tracking_status()

    def select_joints(self):
        if self._is_recording_active():
            return
        if self._stored_joint_selection_map is not None:
            return
        joint_translation_map = self.skeleton_model.get_joint_translation_map()
        segment_joints_map = self.skeleton_model.get_segment_joints_map()
        dlg = KinectJointSelectionDialog(joint_translation_map, dict(self.joint_selection_map), segment_joints_map)
        if dlg.exec():
            self.joint_selection_map = dlg.get_joint_selection_map()
            self.source_controller.set_joint_selection_map(self.joint_selection_map)
            self.config.joint_selection_map = {}
            for joint, selected in self.joint_selection_map.items():
                self.config.joint_selection_map[joint.name] = selected
            self.config_repository.save(self.config)
    def get_fps_range(self):
        return [self.source_controller.min_fps, self.source_controller.max_fps]

    def _get_joints_map_from_config(self):
        selection = self.skeleton_model.generate_joint_selection_map()
        for joint in selection:
            selection[joint] = self.config.joint_selection_map.get(joint.name, True)
        return selection


    def apply_config(self, config: AppConfig):
        if self._is_recording_active():
            raise RuntimeError("Cannot change configuration while recording")
        if config.source_config.source != self.config.source_config.source:
            need_restart = True
        else:
            need_restart = False
        self.config = config
        src_conf, rec_conf = config.source_config, config.recording_config

        self.skeleton_renderer.set_allow_inferred(src_conf.allow_inferred)
        self.biometric_system.set_allow_inferred(src_conf.allow_inferred)
        self.source_controller.configure(allow_inferred=src_conf.allow_inferred, dynamic_tracking=src_conf.dynamic_tracking)
        self.skeleton_renderer.configure(src_conf.allow_inferred)
        self.recording_repository.set_directory(rec_conf.directory)
        self.movement_pattern_repository.set_directory(rec_conf.directory)
        self.recording_controller.configure(rec_conf)
        windows = [self.movement_testing_window, self.registration_window]
        for window in windows:
            if window is not None:
                window.set_fps(config.display_config.fps)
        self.config_repository.save(config)
        return need_restart

    def get_joint_tracking_states(self):
        joints_raw = self.source_controller.source.get_joints_raw()
        if joints_raw is None:
            return None
        joint_states = {}
        for joint, joint_cords in joints_raw.items():
            joint_states[joint] = int(joint_cords[1])
        return joint_states

    def is_movement_pattern_registered(self, movement_name):
        return self.movement_pattern_repository.contains(movement_name)

    def get_movement_pattern_count(self):
        return self.movement_pattern_repository.get_pattern_count()

    def register_movement_pattern(self, movement_name, recording, skeleton_image_recording):
        if self.movement_pattern_repository.contains(movement_name):
            raise ValueError(f"Movement pattern '{movement_name}' is already registered.")
        self.save_recording(recording)
        self.save_recording(skeleton_image_recording)
        pattern = MovementPattern(
            movement_name=movement_name,
            recording_file=f"{recording.recording_id}.json",
            image_recording_file=f"{skeleton_image_recording.recording_id}.json",
            joints=list(recording.metadata.get("joints", [])),
            sample_rate=recording.sample_rate,
            frame_count=len(recording.frames),
            registered_at=datetime.now().isoformat(timespec="seconds")
        )
        self.movement_pattern_repository.add_pattern(pattern)
        return self.movement_pattern_repository.get_pattern_count()

    def get_movement_patterns(self):
        return self.movement_pattern_repository.load_patterns()

    def load_movement_pattern_recording(self, pattern):
        recording_id = os.path.splitext(pattern.image_recording_file)[0]
        recording = self.recording_repository.load_skeleton_recording(recording_id)
        if recording is None:
            raise FileNotFoundError(f"Recording file '{pattern.image_recording_file} does not exist.")
        return recording

    def set_session_joint_selection(self, joint_names):
        names = list(joint_names)
        selection = {}
        for joint in self.joint_selection_map:
            selection[joint] = joint.name in names
        if not any(selection.values()):
            return False
        if self._stored_joint_selection_map is None:
            self._stored_joint_selection_map = dict(self.joint_selection_map)
        self.joint_selection_map = selection
        self.source_controller.set_joint_selection_map(self.joint_selection_map)
        return True

    def restore_joint_selection(self):
        if self._stored_joint_selection_map is None:
            return
        self.joint_selection_map = self._stored_joint_selection_map
        self._stored_joint_selection_map = None
        self.source_controller.set_joint_selection_map(self.joint_selection_map)

    def save_movement_samples(self, samples):
        for recording, skeleton_image_recording in samples:
            self.save_recording(recording)
            self.save_recording(skeleton_image_recording)
        return len(samples)