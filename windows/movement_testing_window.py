from __future__ import annotations

from enum import Enum

import cv2
import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTextEdit, QRadioButton, \
    QLineEdit, QComboBox, QButtonGroup, QGroupBox, QCheckBox
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

from movement.kinect_joints import KinectJoints
from windows.camera_label import CameraLabel


class MeasurementTypes(Enum):
    CORDS_M = "cords_meters",
    CORDS_NORMALIZED = "cords_normalized",
    ANGLES = "angles"

class MovementTestingWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.dynamic_display = False
        self.layout = QVBoxLayout()
        self.display_option = MeasurementTypes.CORDS_NORMALIZED
        btn_menu = QPushButton("Menu Window")
        btn_menu.clicked.connect(self.app_manager.show_menu_window)

        self.layout.addWidget(btn_menu)

        self.generate_layout()
        self.assign_behavior()
        self.setLayout(self.layout)

    def generate_layout(self):
        self.generate_config_panel()
        self.generate_camera_panel()
        self.generate_features_panel()

    def generate_config_panel(self):

        top_bar = QHBoxLayout()
        top_bar.setSpacing(6)

        fps_label = QLabel("FPS:")
        fps_label.setFixedWidth(30)

        self.fps_input = QLineEdit()
        self.fps_input.setPlaceholderText("30")
        self.fps_input.setFixedWidth(55)

        top_bar.addWidget(fps_label)
        top_bar.addWidget(self.fps_input)

        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_pause = QPushButton("Pause")
        self.btn_play = QPushButton("Play")

        for btn in [
            self.btn_start,
            self.btn_stop,
            self.btn_pause,
            self.btn_play
        ]:
            btn.setFixedHeight(28)
            btn.setMinimumWidth(65)

        top_bar.addWidget(self.btn_start)
        top_bar.addWidget(self.btn_stop)
        top_bar.addWidget(self.btn_pause)
        top_bar.addWidget(self.btn_play)

        # Recording
        self.btn_record_start = QPushButton("Rec")
        self.btn_record_stop = QPushButton("Stop Rec")
        self.btn_clear = QPushButton("Clear")
        self.btn_exit = QPushButton("Exit")

        for btn in [
            self.btn_record_start,
            self.btn_record_stop,
            self.btn_clear,
            self.btn_exit
        ]:
            btn.setFixedHeight(28)

        self.dynamic_display_checkbox = QCheckBox(text="Dynamic display")
        self.dynamic_display_checkbox.stateChanged.connect(self.onStateChanged)

        top_bar.addWidget(self.btn_record_start)
        top_bar.addWidget(self.btn_record_stop)
        top_bar.addWidget(self.btn_clear)
        top_bar.addWidget(self.btn_exit)
        top_bar.addWidget(self.dynamic_display_checkbox)


        # Movement select
        self.movement_select = QComboBox()
        self.movement_select.setFixedWidth(150)
        self.movement_select.addItems([
            "Movement 1",
            "Movement 2",
            "Movement 3"
        ])

        top_bar.addWidget(self.movement_select)

        top_bar.addStretch()

        self.layout.addLayout(top_bar)

        mode_bar = QHBoxLayout()
        mode_bar.setSpacing(12)

        self.coord_group = QButtonGroup()

        self.radio_raw = QRadioButton("Meters")
        self.radio_norm = QRadioButton("Normalized")
        self.radio_angles = QRadioButton("Angles")

        self.radio_raw.toggled.connect(
            lambda checked: checked and self.set_display_mode(
                MeasurementTypes.CORDS_M
            )
        )

        self.radio_norm.toggled.connect(
            lambda checked: checked and self.set_display_mode(
                MeasurementTypes.CORDS_NORMALIZED
            )
        )

        self.radio_angles.toggled.connect(
            lambda checked: checked and self.set_display_mode(
                MeasurementTypes.ANGLES
            )
        )

        self.radio_norm.setChecked(True)

        self.coord_group.addButton(self.radio_raw)
        self.coord_group.addButton(self.radio_norm)
        self.coord_group.addButton(self.radio_angles)

        mode_bar.addWidget(QLabel("View:"))
        mode_bar.addWidget(self.radio_raw)
        mode_bar.addWidget(self.radio_norm)
        mode_bar.addWidget(self.radio_angles)
        mode_bar.addStretch()

        self.layout.addLayout(mode_bar)


    def onStateChanged(self):
        self.dynamic_display = self.dynamic_display_checkbox.isChecked()
    def generate_camera_panel(self):

        # Kamera + features obok siebie
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        self.image_label = CameraLabel()
        self.image_label.setFixedSize(700, 520)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            background: #222;
            color: white;
            border: 1px solid #444;
        """)

        content_layout.addWidget(self.image_label)

        self.features_container = content_layout
        self.layout.addLayout(content_layout)

    def generate_features_panel(self):

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFixedSize(440, 520)

        self.text.setStyleSheet("""
            background: #111;
            color: #DDD;
            border: 1px solid #444;
            padding: 6px;
            font-family: Consolas;
            font-size: 12px;
        """)

        self.features_container.addWidget(self.text)



    def assign_behavior(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(33)  # około 30 FPS

    def refresh(self):
        self.refresh_frame()
        self.update_cords_label()
    def refresh_frame(self):
        frame = self.app_manager.get_new_frame()
        # frame = self.app_manager.source_controller.update_frame()
        if frame is not None:
            self.image_label.refresh_frame(frame)


    def set_display_mode(self, mode):

        if self.display_option == mode:
            return

        self.display_option = mode

        for rb in [self.radio_raw, self.radio_norm, self.radio_angles]:
            rb.blockSignals(True)

        self.radio_raw.setChecked(mode == MeasurementTypes.CORDS_M)
        self.radio_norm.setChecked(mode == MeasurementTypes.CORDS_NORMALIZED)
        self.radio_angles.setChecked(mode == MeasurementTypes.ANGLES)

        for rb in [self.radio_raw, self.radio_norm, self.radio_angles]:
            rb.blockSignals(False)

    def update_frame(self, original: np.ndarray):
        self.image_label.update_frame(original)
    def update_cords_label(self):
        lines = []
        self.app_manager.update_joints()
        if self.display_option == MeasurementTypes.CORDS_M:

            for key, value in self.app_manager.get_joint_cords().items():
                lines.append(f"{key.name:>20}:\t{format(value[0], '.4f')}\t{format(value[1], '.4f')}\t{format(value[2], '.4f')}")
            self.text.setText("\n".join(lines))

        elif self.display_option == MeasurementTypes.CORDS_NORMALIZED:
            for key, value in self.app_manager.get_normalized_joints().items():
                lines.append(f"{key.name:>20}:\t{format(value[0], '.4f')}\t{format(value[1], '.4f')}\t{format(value[2], '.4f')}")
            self.text.setText("\n".join(lines))

        elif self.display_option == MeasurementTypes.ANGLES:
            for key, value in self.app_manager.get_angles().items():
                if isinstance(value, str):
                    lines.append(f"{key:>20}:\t{value}")
                else:
                    lines.append(f"{key:>20}:\t{format(value, '.2f')}")
            self.text.setText("\n".join(lines))
        # if self.dynamic_display:
        #     right_hand_up = self.app_manager.source_controller.source.joint_in_range(KinectJoints.HAND_RIGHT, 1.15, 1.71, 0.09, 1, 1, 1)
        #     left_hand_up = self.app_manager.source_controller.source.joint_in_range(KinectJoints.HAND_LEFT, -0.9, 1.68, -0.07, 1, 1, 1)
        #     if right_hand_up and left_hand_up:
        #         self.set_display_mode(MeasurementTypes.CORDS_NORMALIZED)
        #     elif left_hand_up:
        #         self.set_display_mode(MeasurementTypes.CORDS_M)
        #     elif right_hand_up:
        #         self.set_display_mode(MeasurementTypes.ANGLES)
