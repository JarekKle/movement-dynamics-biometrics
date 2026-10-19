from __future__ import annotations

from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

from windows.registration_user_input import RegistrationUserInput


class RegistrationWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.config = self.get_user_input()
        self.generate_layout()
        self.assign_behavior()

    def generate_layout(self):
        layout = QVBoxLayout()

        label = QLabel("This is a Registration Window!")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn_clas = QPushButton("Classification Window")
        btn_clas.clicked.connect(self.app_manager.show_classification_window)

        btn_test = QPushButton("Movement Testing Window")
        btn_test.clicked.connect(self.app_manager.show_movement_testing_window)

        btn_menu = QPushButton("Menu Window")
        btn_menu.clicked.connect(self.app_manager.show_menu_window)

        layout.addWidget(btn_clas)
        layout.addWidget(btn_test)
        layout.addWidget(btn_menu)

        self.setLayout(layout)
    def assign_behavior(self):
        pass
    def get_user_input(self):
        dialog = RegistrationUserInput()

        if dialog.exec():
            if dialog.action == "register":
                print("Register movement:", dialog.movement_name)

            elif dialog.action == "recreate":
                print("Recreate movement for user:", dialog.username)

