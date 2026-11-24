from __future__ import annotations

from enum import Enum

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QHBoxLayout, QTextEdit, QRadioButton, \
    QLineEdit, QButtonGroup, QCheckBox, QSpinBox, QSizePolicy, QGroupBox
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

from domain.recording.recording_state import RecordingState
from sources.tracking_status import TrackingStatus
from ui.camera_label import CameraLabel


class MeasurementTypes(Enum):
    CORDS_M = "cords_meters",
    CORDS_NORMALIZED = "cords_normalized",
    ANGLES = "angles"

class MovementTestingWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.fps = self.app_manager.config.display_config.fps
        self.layout = QVBoxLayout()
        self.display_option = MeasurementTypes.CORDS_NORMALIZED
        self.btn_menu = QPushButton("Menu Window")
        self.btn_menu.clicked.connect(self.app_manager.show_menu_window)

        self.layout.addWidget(self.btn_menu)

        self.generate_layout()
        self.assign_behavior()
        self.setLayout(self.layout)

        self.image_label.setObjectName("cameraView")
        self.text.setObjectName("featuresView")
        self.status_label.setObjectName("statusLabel")
    def generate_layout(self):
        self.generate_config_panel()
        self.generate_camera_panel()
        self.generate_status_label()
        self.generate_features_panel()

    def generate_status_label(self):
        self.status_label = QLabel("Initializing source...")
        self.layout.addWidget(self.status_label)
        self.update_status_label(TrackingStatus.SOURCE_DISCONNECTED,RecordingState.NOT_RECORDING,0)
    def generate_config_panel(self):
        src_box = QGroupBox("Source")
        src_row = QHBoxLayout(src_box)

        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_open = QPushButton("Open")
        self.btn_close = QPushButton("Close")

        for btn in [
            self.btn_start,
            self.btn_stop,
            self.btn_open,
            self.btn_close
        ]:
            src_row.addWidget(btn)

        rec_box = QGroupBox("Recording")
        rec_row = QHBoxLayout(rec_box)
        self.btn_record_start = QPushButton("Rec")
        self.btn_record_stop = QPushButton("Stop Rec")
        self.btn_record_stop.setEnabled(False)
        self.btn_joint_select = QPushButton("Select joints")

        for btn in [
            self.btn_record_start,
            self.btn_record_stop,
            self.btn_joint_select,
        ]:
            rec_row.addWidget(btn)

        mode_box = QGroupBox("View")
        mode_row = QHBoxLayout(mode_box)


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

        mode_row.addWidget(self.radio_raw)
        mode_row.addWidget(self.radio_norm)
        mode_row.addWidget(self.radio_angles)


        top_bar = QHBoxLayout()
        top_bar.addWidget(src_box)
        top_bar.addWidget(rec_box)
        top_bar.addWidget(mode_box)
        top_bar.addStretch()
        self.layout.addLayout(top_bar)

    def generate_camera_panel(self):

        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        self.image_label = CameraLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(320, 180)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        content_layout.addWidget(self.image_label, stretch=3)

        self.features_container = content_layout
        self.layout.addLayout(content_layout, stretch=1)

    def generate_features_panel(self):

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        self.text.setMinimumWidth(260)

        self.features_container.addWidget(self.text)



    def assign_behavior(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000 // self.fps)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.refresh_tracking_status)
        self.status_timer.start(1000)
        # self.btn_apply_fps.clicked.connect(self.set_fps)
        self.btn_stop.clicked.connect(self.stop_source)
        self.btn_start.clicked.connect(self.start_source)
        self.btn_open.clicked.connect(self.open_source)
        self.btn_close.clicked.connect(self.close_source)
        self.btn_record_start.clicked.connect(self.record_start)
        self.btn_record_stop.clicked.connect(self.record_stop)

        self.btn_joint_select.clicked.connect(self.select_joints)

    def set_fps(self, fps):
            self.fps = fps
            self.timer.setInterval(1000 // self.fps)
    def get_fps_range(self):
        return self.app_manager.get_fps_range()
    def stop_source(self):
        self.app_manager.stop_source()
    def start_source(self):
        self.app_manager.start_source()

    def open_source(self):
        self.app_manager.open_source()

    def close_source(self):
        self.app_manager.close_source()

    def record_start(self):
        # status = self.refresh_tracking_status()
        # if status == TrackingStatus.ALL_REQUIRED_JOINTS_TRACKED:
        self.app_manager.start_recording()
        self.set_recording_controls_locked(True)
    def set_recording_controls_locked(self, locked):
        self.btn_record_start.setEnabled(not locked)
        self.btn_record_stop.setEnabled(locked)
        # self.btn_apply_fps.setEnabled(not locked)
        self.btn_stop.setEnabled(not locked)
        self.btn_start.setEnabled(not locked)
        self.btn_close.setEnabled(not locked)
        self.btn_joint_select.setEnabled(not locked)
        self.btn_open.setEnabled(not locked)
        self.btn_menu.setEnabled(not locked)
    def record_stop(self):
        self.app_manager.stop_recording()
        self.set_recording_controls_locked(False)

    def refresh(self):
        self.refresh_frame()
        self.update_cords_label()
    def refresh_frame(self):
        frame = self.app_manager.get_new_frame()
        # frame = self.app_manager.source_controller.update_frame()
        if frame is not None:
            self.image_label.refresh_frame(frame)

    def select_joints(self):
        self.app_manager.select_joints()

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

    def update_status_label(self, source_status, recording_status, remaining_seconds):
        label_source_text = {
            TrackingStatus.SOURCE_DISCONNECTED: "Source disconnected",
            TrackingStatus.SOURCE_READY: "Source ready",
            TrackingStatus.NO_PEOPLE_TRACKED: "No person detected!",
            TrackingStatus.TOO_MANY_PEOPLE_TRACKED: "Too many people detected!",
            TrackingStatus.ALL_REQUIRED_JOINTS_TRACKED: "Everything OK",
            TrackingStatus.REQUIRED_JOINTS_NOT_TRACKED: "Missing required joints! Correct your position!",
            TrackingStatus.PERSON_LOST: "Unable to track person",
            TrackingStatus.ERROR: "An error occurred with the source",
            TrackingStatus.SOURCE_PAUSED: "Source paused",
            RecordingState.RECORDING: "Recording movements",
            RecordingState.COUNTING_DOWN: f"Recording in: {remaining_seconds}s",
            RecordingState.FINISHED_RECORDING: "Recording done!",
            RecordingState.CANCELLED_RECORDING: "Recording cancelled!"
        }
        self.status_label.setText(label_source_text.get(recording_status,label_source_text.get(source_status,"Unknown status")))
    def refresh_tracking_status(self):
        source_status = self.app_manager.get_tracking_status()
        recording_status = self.app_manager.get_recording_status()
        remaining_seconds = self.app_manager.get_recording_countdown_seconds()
        self.update_status_label(source_status, recording_status, remaining_seconds)
        self.set_recording_controls_locked(recording_status in (RecordingState.RECORDING, RecordingState.COUNTING_DOWN))

        return source_status
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
