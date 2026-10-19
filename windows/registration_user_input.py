
from PyQt6.QtWidgets import (
    QDialog,
    QPushButton,
    QVBoxLayout,
    QInputDialog,
    QMessageBox,
)


class RegistrationUserInput(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

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
        name, accepted = QInputDialog.getText(
            self,
            "Give name",
            "Enter movement name:",
        )

        if not accepted:
            return

        name = name.strip()
        if not name:
            QMessageBox.warning(
                self, "Invalid name", "Movement name cannot be empty."
            )
            return

        self.movement_name = name
        self.action = "register"
        self.accept()

    def ask_for_username(self):
        username, accepted = QInputDialog.getText(
            self,
            "Give username",
            "Enter username:",
        )

        if not accepted:
            return

        username = username.strip()
        if not username:
            QMessageBox.warning(
                self, "Invalid username", "Username cannot be empty."
            )
            return

        self.username = username
        self.action = "recreate"
        self.accept()
