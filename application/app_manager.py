from __future__ import annotations

from enum import Enum

from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout

from biometric.biometric_system import BiometricSystem
from domain.movement.kinect.kinect_skeleton_model import KinectSkeletonModel
from application.json_recording_repository import JsonRecordingRepository
from application.recording_controller import RecordingController
from sources.kinect.kinect_skeleton_renderer import KinectSkeletonRenderer
from sources.kinect.kinect_source import KinectSource
from sources.source_controller import SourceController
from sources.source_registry import SourceRegistry
from ui.windows.classification_window import ClassificationWindow
from ui.kinect_joint_selection_dialog import KinectJointSelectionDialog
from ui.windows.menu_window import MenuWindow
from ui.windows.movement_testing_window import MovementTestingWindow
from ui.windows.registration_window import RegistrationWindow


class AppStates(Enum):
    MENU = 0,
    REGISTRATION = 1,
    CLASSIFICATION = 2,
    TESTING = 3


class AppManager(QWidget):
    def __init__(self, source: SourceRegistry, recording_path):
        """
        Initialize an AppManager object.
        :param source: source that defines how the joints are processed
        :type source: SourceRegistry
        :param recording_path: path to a directory where recordings are uploaded
        :type recording_path: str
        """
        super().__init__()
        self._allow_inferred = False
        self._dynamic_tracking = True
        if source == SourceRegistry.KINECT:
            self.skeleton_renderer = KinectSkeletonRenderer(self._allow_inferred)
            self.source = KinectSource()
            self.skeleton_model = KinectSkeletonModel()
        self.joint_selection_map = self.skeleton_model.generate_joint_selection_map()
        self.setWindowTitle("Movement dynamics biometrics")

        self.stack = QStackedWidget()

        self.biometric_system = BiometricSystem(self.skeleton_model, self._allow_inferred)
        self.source_controller = SourceController(self.source, self.skeleton_renderer, self._dynamic_tracking,
                                                  self._allow_inferred, self.joint_selection_map)

        self.recording_repository = JsonRecordingRepository(recording_path)
        self.recording_controller = RecordingController(self.source_controller, self.recording_repository, 1 / 30)

        self.menu_window = MenuWindow(self)
        self._app_state = AppStates.MENU
        self.movement_testing_window = None
        self.registration_window = None
        self.classification_window = None
        self.classification_results_page = None

        self.stack.addWidget(self.menu_window)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def start_recording(self):
        """
        Activate a method in the recording controller to start recording.
        :return:
        """
        if self.recording_controller.is_recording():
            return
        self.recording_controller.start_recording()

    def stop_recording(self):
        """
        Activate a method in the recording controller to stop recording.
        :return: A dictionary of recorded joints and a dictionary of joints position on the screen.
        :rtype: dict
        """
        recording, skeleton_image_recording = self.recording_controller.stop_recording()
        if recording is not None:
            self.last_recording = recording
        if skeleton_image_recording is not None:
            self.last_skeleton_image_recording = skeleton_image_recording
        return recording, skeleton_image_recording

    def save_recording(self, recording=None):
        """
        :param recording: A dictionary of recorded joints obtained from method AppManager.stop_recording() (could either be a recording or a skeleton image recording).
        :type recording: dict
        :return:
        """
        recording = recording or self.last_recording
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
        self.source_controller.source.close()
        self.stack.setCurrentWidget(self.menu_window)
        self._app_state = AppStates.MENU

    def show_movement_testing_window(self):
        """
        Sets currently displayed window to Movement testing window and changed app's state to AppStates.TESTING
        """
        self.source_controller.source.open()

        if self.movement_testing_window is None:
            self.movement_testing_window = MovementTestingWindow(self)
            self.stack.addWidget(self.movement_testing_window)
        self.stack.setCurrentWidget(self.movement_testing_window)
        self._app_state = AppStates.TESTING

    def show_registration_window(self):
        """
        Sets currently displayed window to Registration window and changed app's state to AppStates.REGISTRATION
        """
        self.source_controller.source.open()
        if self.registration_window is None:
            self.registration_window = RegistrationWindow(self)
            self.stack.addWidget(self.registration_window)
        self.stack.setCurrentWidget(self.registration_window)
        self._app_state = AppStates.REGISTRATION

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

    def get_new_frame(self):
        """
        Receives new frame from a source controller and passes it to recording controller, if currently recording.
        :return: New color frame received from source controller.
        :rtype: ndarray
        """
        new_frame = self.source_controller.update_frame(self._dynamic_tracking)
        if self.recording_controller.is_recording():
            body = self.source_controller.get_joints_as_skeleton_frame()
            joints_2d = self.source_controller.get_joints_2d_selected()
            self.recording_controller.add_frame(body)
            self.recording_controller.add_image_frame(joints_2d)

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
        joint_translation_map = self.skeleton_model.get_joint_translation_map()
        bones_translation_map = self.skeleton_model.get_bones_translation_map()
        dlg = KinectJointSelectionDialog(joint_translation_map, self.joint_selection_map, bones_translation_map)
        if dlg.exec():
            self.joint_selection_map = dlg.get_joint_selection_map()
            self.source_controller.set_joint_selection_map(self.joint_selection_map)
