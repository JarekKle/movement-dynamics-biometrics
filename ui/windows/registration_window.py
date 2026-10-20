from __future__ import annotations

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QTextEdit

from domain.recording.recording_state import RecordingState
from sources.tracking_status import TrackingStatus
from ui.camera_label import CameraLabel
from ui.registration_user_input import RegistrationUserInput


class RegistrationWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.movement_name = None
        self.username = None
        self.action = None
        self.layout = QVBoxLayout()
        self.fps = 30

        self.get_user_input()
        self.generate_layout()
        self.assign_behavior()

    def generate_layout(self):
        self.generate_config_panel()
        self.generate_camera_panel()
        self.generate_tracking_state_panel()
        self.generate_status_label()
        btn_menu = QPushButton("Menu Window")
        btn_menu.clicked.connect(self.app_manager.show_menu_window)

        self.layout.addWidget(btn_menu)

        self.setLayout(self.layout)
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
        self.btn_apply_fps = QPushButton("OK")
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")

        for btn in [
            self.btn_apply_fps,
            self.btn_start,
            self.btn_stop,
        ]:
            btn.setFixedHeight(28)
            btn.setMinimumWidth(65)
            top_bar.addWidget(btn)

        # Recording
        self.btn_record_start = QPushButton("Rec")
        self.btn_record_stop = QPushButton("Stop Rec")
        self.btn_record_stop.setEnabled(False)

        for btn in [
            self.btn_record_start,
            self.btn_record_stop,
        ]:
            btn.setFixedHeight(28)
            top_bar.addWidget(btn)

        # Movement select

        top_bar.addStretch()

        self.layout.addLayout(top_bar)

        mode_bar = QHBoxLayout()
        mode_bar.setSpacing(12)
    def generate_camera_panel(self):

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

    def generate_tracking_state_panel(self):

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

    def generate_status_label(self):
        self.status_label = QLabel("Initializing source...")
        self.status_label.setFixedHeight(15)
        self.layout.addWidget(self.status_label)
        self.update_status_label(TrackingStatus.PERSON_LOST)
    def assign_behavior(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000 // self.fps)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.refresh_tracking_status)
        self.status_timer.start(1000)
        self.btn_apply_fps.clicked.connect(self.set_fps)
        self.btn_stop.clicked.connect(self.stop_source)
        self.btn_start.clicked.connect(self.start_source)
        self.btn_record_start.clicked.connect(self.record_start)
        self.btn_record_stop.clicked.connect(self.record_stop)
    def set_fps(self):
        try:
            self.fps = int(self.fps_input.text())
            self.timer.setInterval(1000 // self.fps)
        except:
            print("Wrong fps value")
    def stop_source(self):
        self.app_manager.stop_source()
    def start_source(self):
        self.app_manager.start_source()
    def record_start(self):
        status = self.refresh_tracking_status()
        if status == TrackingStatus.ALL_REQUIRED_JOINTS_TRACKED:
            self.app_manager.start_recording()
            self.btn_record_start.setEnabled(False)
            self.btn_record_stop.setEnabled(True)
    def record_stop(self):
        recording = self.app_manager.stop_recording()
        if recording is not None:
            self.app_manager.save_recording(recording)
        self.btn_record_start.setEnabled(True)
        self.btn_record_stop.setEnabled(False)
    def refresh(self):
        self.refresh_frame()
    def refresh_frame(self):
        frame = self.app_manager.get_new_frame()
        # frame = self.app_manager.source_controller.update_frame()
        if frame is not None:
            self.image_label.refresh_frame(frame)
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
        return source_status
    def select_joints(self):
        self.app_manager.select_joints()
    def get_joint_selection_map(self):
        self.app_manager.get_joint_selection_map()

    def get_user_input(self):
        dialog = RegistrationUserInput(self)

        if dialog.exec():
            self.movement_name = dialog.movement_name
            self.username = dialog.username
            self.action = dialog.action

