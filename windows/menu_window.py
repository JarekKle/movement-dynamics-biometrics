from __future__ import annotations

from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel


class MenuWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager

        layout = QVBoxLayout()

        label = QLabel("This is a Menu Window!")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn_test = QPushButton("Testing Window")
        btn_test.clicked.connect(self.app_manager.show_movement_testing_window)

        btn_reg = QPushButton("Registration Window")
        btn_reg.clicked.connect(self.app_manager.show_registration_window)

        btn_clas = QPushButton("Classification Window")
        btn_clas.clicked.connect(self.app_manager.show_classification_window)

        layout.addWidget(btn_test)
        layout.addWidget(btn_reg)
        layout.addWidget(btn_clas)

        self.setLayout(layout)