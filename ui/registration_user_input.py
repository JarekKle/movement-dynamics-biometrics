
from PyQt6.QtWidgets import (QDialog,QPushButton,QVBoxLayout,QInputDialog,QMessageBox)

from domain.recording.recording_action import RecordingAction
from ui.sample_registration_form import SampleRegistrationForm


class RegistrationUserInput(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Movement registration")
        self.movement_name = None
        self.username = None
        self.action = None
        self.pattern = None
        self.sample_count = 1

        self.btn_register = QPushButton("Register new movement")
        self.btn_recreate = QPushButton("Recreate existing movement")

        self.btn_register.clicked.connect(self.ask_for_movement_name)
        self.btn_recreate.clicked.connect(self.ask_for_username)

        layout = QVBoxLayout(self)
        layout.addWidget(self.btn_register)
        layout.addWidget(self.btn_recreate)

    def ask_for_movement_name(self):
        name, ok = QInputDialog.getText(self,"Enter movement name","Movement name (ex. left hand wave, running in place):")
        if not ok:
            return
        name = name.strip()
        if not name:
            QMessageBox.warning(self, "Invalid name", "Please provide a movement name.")
            return
        self.movement_name = name
        self.action = RecordingAction.REGISTER
        self.accept()
        self.ask_for_enabled_joints()
    def ask_for_enabled_joints(self):
        self.parent.select_joints()

    def ask_for_username(self):
        app_manager = self.parent.app_manager
        try:
            patterns = app_manager.get_movement_patterns()
        except ValueError as error:
            QMessageBox.critical(self, "Movement pattern index", str(error))
            return
        if not patterns:
            QMessageBox.information(self, "No movement patterns",
                                    "No movement pattern has been registered yet. Register a new movement first.")
            return
        form = SampleRegistrationForm(patterns, app_manager.config.recording_config.samples_per_session, self)
        if not form.exec():
            return
        self.username = form.get_username()
        self.pattern = form.get_pattern()
        self.movement_name = self.pattern.movement_name
        self.sample_count = form.get_sample_count()
        self.action = RecordingAction.RECREATE
        self.accept()
