
from PyQt6.QtWidgets import (QDialog,QPushButton,QVBoxLayout,QInputDialog,QMessageBox)

from domain.recording.recording_action import RecordingAction


class RegistrationUserInput(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Movement registration")
        self.movement_name = None
        self.username = None
        self.action = None

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
        if not name:
            QMessageBox.warning(self, "Invalid name", "Please provide a movement name.")
            return
        self.movement_name = name.strip()
        self.action = RecordingAction.REGISTER
        self.accept()
        self.ask_for_enabled_joints()
    def ask_for_enabled_joints(self):
        self.parent.select_joints()

    def ask_for_username(self):
        username, ok = QInputDialog.getText(self,"Enter your username","Your username:")
        if not ok:
            return
        if not username:
            QMessageBox.warning(self, "Invalid username", "Please provide your username.")
            return
        self.username = username.strip()
        self.action = RecordingAction.RECREATE
        self.accept()
