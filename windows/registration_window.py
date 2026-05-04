from __future__ import annotations

from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel


class RegistrationWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager

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