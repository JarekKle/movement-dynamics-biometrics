from __future__ import annotations

from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout

from sources.kinect_source import KinectSource
from sources.source_controller import SourceController
from windows.classification_window import ClassificationWindow
from windows.menu_window import MenuWindow
from windows.movement_testing_window import MovementTestingWindow
from windows.registration_window import RegistrationWindow


class AppManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movement dynamics biometrics")

        self.stack = QStackedWidget()

        self.kinect_controller = SourceController(KinectSource())
        self.menu_window = MenuWindow(self)
        self.movement_testing_window = None
        self.registration_window = None
        self.classification_window = None
        self.classification_results_page = None

        self.stack.addWidget(self.menu_window)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def show_menu_window(self):
        self.kinect_controller.source.close()
        self.stack.setCurrentWidget(self.menu_window)

    def show_movement_testing_window(self):
        self.kinect_controller.source.open()

        if self.movement_testing_window is None:
            self.movement_testing_window = MovementTestingWindow(self)
        self.stack.addWidget(self.movement_testing_window)
        self.stack.setCurrentWidget(self.movement_testing_window)

    def show_registration_window(self):
        self.kinect_controller.source.close()
        if self.registration_window is None:
            self.registration_window = RegistrationWindow(self)
        self.stack.addWidget(self.registration_window)
        self.stack.setCurrentWidget(self.registration_window)

    def show_classification_window(self):
        self.kinect_controller.source.close()
        if self.classification_window is None:
            self.classification_window = ClassificationWindow(self)
        self.stack.addWidget(self.classification_window)
        self.stack.setCurrentWidget(self.classification_window)
