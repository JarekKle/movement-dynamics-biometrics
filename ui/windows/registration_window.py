from __future__ import annotations

import html
import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QTextEdit, QSpinBox, \
    QGroupBox, QSizePolicy, QMessageBox

from domain.recording.recording_action import RecordingAction
from domain.recording.recording_state import RecordingState
from sources.tracking_status import TrackingStatus
from ui.camera_label import CameraLabel
from ui.movement_pattern_preview_dialog import MovementPatternPreviewDialog
from ui.registration_user_input import RegistrationUserInput


class RegistrationWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.movement_name = None
        self.username = None
        self.action = None
        self.layout = QVBoxLayout()
        self.fps = self.app_manager.config.display_config.fps
        self.last_source_status = TrackingStatus.SOURCE_DISCONNECTED
        self._last_panel = None
        self.generate_layout()
        self.assign_behavior()


        self.joint_state_styles = {
            2: ("#4bae4f", "tracked"),
            1: ("#feb200", "inferred"),
            0: ("#e43834", "not tracked"),
        }
        self.joint_inactive_style = ("#5e6267", "not selected")
        self.no_joint_data_style = ("#5e6267", "no data")

        self.source_status_styles = {
            TrackingStatus.ALL_REQUIRED_JOINTS_TRACKED: "#4bae49",
            TrackingStatus.REQUIRED_JOINTS_NOT_TRACKED: "#feb200",
            TrackingStatus.NO_PEOPLE_TRACKED: "#feb200",
            TrackingStatus.TOO_MANY_PEOPLE_TRACKED: "#feb200",
            TrackingStatus.PERSON_LOST: "#feb200",
            TrackingStatus.SOURCE_PAUSED: "#feb200",
        }
        self.source_status_default_color = "#e43834"
    def generate_layout(self):
        self.generate_config_panel()
        self.generate_camera_panel()
        self.generate_tracking_state_panel()
        self.generate_status_label()
        self.btn_menu = QPushButton("Menu Window")
        self.btn_menu.clicked.connect(self.app_manager.show_menu_window)

        self.layout.addWidget(self.btn_menu)

        self.setLayout(self.layout)
        self.image_label.setObjectName("cameraView")
        self.text.setObjectName("featuresView")
        self.status_label.setObjectName("statusLabel")

    def generate_config_panel(self):
        self.movement_label = QLabel()
        self.movement_label.setObjectName("movementNameLabel")

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


        top_bar = QHBoxLayout()
        top_bar.addWidget(self.movement_label)
        top_bar.addWidget(rec_box)
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

    def generate_tracking_state_panel(self):

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        self.text.setMinimumWidth(260)

        self.features_container.addWidget(self.text)


    def generate_status_label(self):
        self.status_label = QLabel("Initializing source...")
        self.layout.addWidget(self.status_label)
        self.update_status_label(TrackingStatus.SOURCE_DISCONNECTED, RecordingState.NOT_RECORDING, 0)
    def assign_behavior(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000 // self.fps)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.refresh_tracking_status)
        self.status_timer.start(1000)
        # self.btn_apply_fps.clicked.connect(self.set_fps)
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
    def record_start(self):
        self.app_manager.start_recording(self.prepare_metadata())
        self.set_recording_controls_locked(True)
    def record_stop(self):
        self.app_manager.stop_recording()
        self.set_recording_controls_locked(False)
    def set_recording_controls_locked(self, locked):
        self.btn_record_start.setEnabled(not locked)
        self.btn_record_stop.setEnabled(locked)
        # self.btn_apply_fps.setEnabled(not locked)
        self.btn_menu.setEnabled(not locked)
        self.btn_joint_select.setEnabled(not locked)
    def refresh(self):
        self.refresh_frame()
        self.update_tracking_panel()
    def refresh_frame(self):
        frame = self.app_manager.get_new_frame()
        # frame = self.app_manager.source_controller.update_frame()
        if frame is not None:
            self.image_label.refresh_frame(frame)
    def update_frame(self, original: np.ndarray):
        self.image_label.update_frame(original)

    def _get_status_texts(self, remaining_seconds=0):
        return {
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

    def update_status_label(self, source_status, recording_status, remaining_seconds):
        label_source_text = self._get_status_texts(remaining_seconds)
        self.status_label.setText(label_source_text.get(recording_status,
                                                        label_source_text.get(source_status,
                                                                              "Unknown status")))
    def refresh_tracking_status(self):
        source_status = self.app_manager.get_tracking_status()
        recording_status = self.app_manager.get_recording_status()
        remaining_seconds = self.app_manager.get_recording_countdown_seconds()
        self.update_status_label(source_status, recording_status, remaining_seconds)
        self.set_recording_controls_locked(recording_status in (RecordingState.RECORDING, RecordingState.COUNTING_DOWN))
        return source_status
    def select_joints(self):
        self.app_manager.select_joints()
    def get_joint_selection_map(self):
        self.app_manager.get_joint_selection_map()

    def get_user_input(self):
        dialog = RegistrationUserInput(self)
        if not dialog.exec():
            return False
        if dialog.action == RecordingAction.REGISTER:
            self.movement_name = dialog.movement_name
            self.username = dialog.username
            self.action = dialog.action

    def update_tracking_panel(self):
        joint_states = self.app_manager.get_joint_tracking_states()
        joint_selection_map = self.app_manager.get_joint_selection_map()
        allow_inferred = self.app_manager.config.source_config.allow_inferred

        status_text = self._get_status_texts().get(self.last_source_status, "Unknown status")
        status_color = self.source_status_styles.get(self.last_source_status, self.source_status_default_color)

        rows = []
        selected_count = 0
        accepted_count = 0
        joint_translation_map = self.app_manager.skeleton_model.get_joint_translation_map()
        for joint_name, joint in joint_translation_map.items():
            if not joint_selection_map.get(joint, False):
                color, desc = self.joint_inactive_style
            else:
                selected_count += 1
                if not joint_states:
                    color, desc = self.no_joint_data_style
                else:
                    state = joint_states.get(joint, 0)
                    color, desc = self.joint_state_styles.get(state, self.joint_state_styles[0])
                    if state == 2:
                        accepted_count += 1
                    elif state == 1 and allow_inferred:
                        accepted_count += 1
            rows.append(
                f"<tr><td>{html.escape(joint_name)}</td>"
                f"<td style='color:{color}'>{desc}</td></tr>"
            )
        if allow_inferred:
            inferred_info = "OK"
        else:
            inferred_info = "NOT OK"
        panel = (
            f"<p><b>Source:</b> <span style='color:{status_color}'>{html.escape(status_text)}</span></p>"
            f"<p><b>Required joint count:</b> {accepted_count}/{selected_count}</p>"
            f"<table cellspacing='0' cellpadding='1'>{''.join(rows)}</table>"
            f"<p style='color:#898c92'>"
            f"tracked &nbsp; inferred ({inferred_info}) &nbsp; not tracked &nbsp; not selected</p>"
        )
        if panel != self._last_panel:
            self.text.setHtml(panel)
            self._last_panel = panel
    def get_user_input(self):
        dialog = RegistrationUserInput(self)
        if not dialog.exec():
            return False
        if dialog.action == RecordingAction.REGISTER:
            try:
                is_movement_registered = self.app_manager.is_movement_pattern_registered(dialog.movement_name)
            except ValueError as e:
                QMessageBox.critical(self, "Movement pattern index", str(e))
                return False
            if is_movement_registered:
                QMessageBox.warning(self, "Movement already registered",
                                    f"Movement pattern '{dialog.movement_name} already exists.")
                return False
        self.movement_name = dialog.movement_name
        self.username = dialog.username
        self.action = dialog.action
        self.update_movement_info()
        return True

    def update_movement_info(self):
        if self.action == RecordingAction.REGISTER:
            self.movement_label.setText(f"Registering movement: {self.movement_name}")
        elif self.action == RecordingAction.RECREATE:
            self.movement_label.setText(f"Recreating movement {self.movement_name}, user: {self.username}")
        else:
            self.movement_label.setText("")
        self.btn_joint_select.setVisible(self.action == RecordingAction.REGISTER)

    def prepare_metadata(self):
        selected_joints = []
        for joint, selected in self.app_manager.get_joint_selection_map().items():
            if selected:
                selected_joints.append(joint.name)
        if self.action is not None:
            action = self.action.name
        else:
            action = None

        return {
            "action": action,
            "movement_name": self.movement_name,
            "username": self.username,
            "joints": selected_joints,
        }

    def handle_recording_finish(self, recording, skeleton_image_recording):
        if self.action != RecordingAction.REGISTER:
            self.app_manager.save_recording(recording)
            self.app_manager.save_recording(skeleton_image_recording)
            return

        QTimer.singleShot(0, lambda: self.review_recording(recording, skeleton_image_recording))

    def review_recording(self, recording, skeleton_image_recording):
        self.timer.stop()
        dialog = MovementPatternPreviewDialog(self.app_manager.skeleton_renderer, skeleton_image_recording,
                                             self.movement_name, self)
        accepted = dialog.exec()
        self.timer.start(1000 // self.fps)
        if not accepted:
            self.status_label.setText("Recording discarded. Record again.")
            return
        try:
            pattern_count = self.app_manager.register_movement_pattern(self.movement_name, recording,
                                                                       skeleton_image_recording)
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Cannot register movement pattern", str(error))
            return
        QMessageBox.information(self, "Movement pattern registered",
                                f"Movement pattern '{self.movement_name}' has been registered.")
        self.app_manager.show_menu_window()
