from __future__ import annotations

from enum import Enum

from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout

from biometric.biometric_system import BiometricSystem
from movement.kinect_skeleton_model import KinectSkeletonModel
from sources.kinect_skeleton_renderer import KinectSkeletonRenderer
from sources.kinect_source import KinectSource
from sources.source_controller import SourceController
from sources.sources import Sources
from windows.classification_window import ClassificationWindow
from windows.kinect_joint_selection_dialog import KinectJointSelectionDialog
from windows.menu_window import MenuWindow
from windows.movement_testing_window import MovementTestingWindow
from windows.registration_window import RegistrationWindow

class AppStates(Enum):
    MENU = 0,
    REGISTRATION = 1,
    CLASSIFICATION = 2,
    TESTING = 3

class AppManager(QWidget):
    def __init__(self, source: Sources):
        super().__init__()
        self._allow_inferred = True
        self._dynamic_tracking = True
        if source == Sources.KINECT:
            self.skeleton_renderer = KinectSkeletonRenderer(self._allow_inferred)
            self.source = KinectSource()
            self.skeleton_model = KinectSkeletonModel()
        self.joint_selection_map = self.skeleton_model.generate_joint_selection_map()
        self.setWindowTitle("Movement dynamics biometrics")

        self.stack = QStackedWidget()

        self.biometric_system = BiometricSystem(self.skeleton_model, self._allow_inferred)
        self.source_controller = SourceController(self.source, self.skeleton_renderer, self._dynamic_tracking)

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

    def assign_menu_behavior(self):
        pass
    def assign_registration_window_behavior(self):
        pass
    def assign_classification_window_behavior(self):
        pass
    def assign_testing_window_behavior(self):
        pass
    def state_manager(self):
        match self._app_state:
            case AppStates.MENU:
                self.assign_menu_behavior()
            case AppStates.REGISTRATION:
                self.assign_registration_window_behavior()
            case AppStates.CLASSIFICATION:
                self.assign_classification_window_behavior()
            case AppStates.TESTING:
                self.assign_testing_window_behavior()


    def show_menu_window(self):
        self.source_controller.source.close()
        self.stack.setCurrentWidget(self.menu_window)
        self._app_state = AppStates.MENU

    def show_movement_testing_window(self):
        self.source_controller.source.open()

        if self.movement_testing_window is None:
            self.movement_testing_window = MovementTestingWindow(self)
            self.stack.addWidget(self.movement_testing_window)
        self.stack.setCurrentWidget(self.movement_testing_window)
        self._app_state = AppStates.TESTING


    def show_registration_window(self):
        self.source_controller.source.close()
        if self.registration_window is None:
            self.registration_window = RegistrationWindow(self)
            self.stack.addWidget(self.registration_window)
        self.stack.setCurrentWidget(self.registration_window)
        self._app_state = AppStates.REGISTRATION


    def show_classification_window(self):
        self.source_controller.source.close()
        if self.classification_window is None:
            self.classification_window = ClassificationWindow(self)
            self.stack.addWidget(self.classification_window)
        self.stack.setCurrentWidget(self.classification_window)
        self._app_state = AppStates.CLASSIFICATION

    def get_new_frame(self):
        return self.source_controller.update_frame(self._dynamic_tracking)
    def get_normalized_joints(self):
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
        return self.source_controller.get_tracking_status(
        )
    def select_joints(self):
        joint_translation_map = self.skeleton_model.get_joint_translation_map()
        dlg = KinectJointSelectionDialog(joint_translation_map, self.joint_selection_map)
        if dlg.exec():
            self.joint_selection_map = dlg.get_joint_selection_map()
