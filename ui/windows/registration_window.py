from __future__ import annotations

import html
from uuid import uuid4

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
        self.pattern = None
        self.sample_count = 1
        self.samples = []
        self.session_id = None
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
        self.btn_menu.clicked.connect(self.go_to_menu_prompted)

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
        self.btn_view_pattern = QPushButton("View pattern")
        self.btn_finish = QPushButton("Finish (0/0)")

        for btn in [
            self.btn_record_start,
            self.btn_record_stop,
            self.btn_joint_select,
            self.btn_view_pattern,
            self.btn_finish
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
        self.btn_view_pattern.clicked.connect(self.view_pattern)
        self.btn_finish.clicked.connect(self.finish_session)

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
        self.btn_view_pattern.setEnabled(not locked)
        self.btn_finish.setEnabled(not locked and len(self.samples) > 0)


    def refresh(self):
        import time
        start = time.perf_counter()
        self.refresh_frame()
        self.update_tracking_panel()
        elapsed = (time.perf_counter() - start) * 1000
        if elapsed > 1000 / self.fps:
            print(f"refresh took {elapsed:.1f} ms (budget {1000 / self.fps:.1f} ms)")
    def refresh_frame(self):
        frame = self.app_manager.get_new_frame(self.image_label.get_target_size())
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
        self.last_source_status = source_status
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
        self.pattern = dialog.pattern
        self.sample_count = dialog.sample_count
        self.samples = []
        self.session_id = None
        if self.action == RecordingAction.RECREATE:
            self.session_id = str(uuid4())
            if not self.app_manager.set_session_joint_selection(self.pattern.joints):
                QMessageBox.warning(self, "Movement pattern joints",
                                    f"Movement pattern '{self.movement_name}' has no joint list. "
                                    "The current joint selection is used.")
        self.update_movement_info()
        return True

    def update_movement_info(self):
        if self.action == RecordingAction.REGISTER:
            self.movement_label.setText(f"Registering movement: {self.movement_name}")
        elif self.action == RecordingAction.RECREATE:
            current_sample = min(len(self.samples) + 1, self.sample_count)
            self.movement_label.setText(f"Recreating movement {self.movement_name}, user: {self.username}, "
                                        f"sample {current_sample}/{self.sample_count}")
        else:
            self.movement_label.setText("")
        self.btn_joint_select.setVisible(self.action == RecordingAction.REGISTER)
        self.btn_view_pattern.setVisible(self.action == RecordingAction.RECREATE)
        self.btn_finish.setVisible(self.action == RecordingAction.RECREATE)
        self.btn_finish.setText(f"Finish ({len(self.samples)}/{self.sample_count})")
        self.btn_finish.setEnabled(len(self.samples) > 0 and not self._is_recording_active())

    def prepare_metadata(self):
        selected_joints = []
        for joint, selected in self.app_manager.get_joint_selection_map().items():
            if selected:
                selected_joints.append(joint.name)
        if self.action is not None:
            action = self.action.name
        else:
            action = None

        metadata = {
            "action": action,
            "movement_name": self.movement_name,
            "username": self.username,
            "joints": selected_joints,
        }
        if self.acton == RecordingAction.RECREATE:
            metadata["session_id"] = self.session_id
            metadata["sample_index"] = len(self.samples) + 1
            metadata["sample_count"] = self.sample_count
            metadata["pattern_recording_file"] = self.pattern.recording_file
        return metadata

    def handle_recording_finish(self, recording, skeleton_image_recording):
        if self.action == RecordingAction.REGISTER:
            QTimer.singleShot(0, lambda: self.review_recording(recording, skeleton_image_recording))
        elif self.action == RecordingAction.RECREATE:
            QTimer.singleShot(0, lambda: self.review_sample(recording, skeleton_image_recording))
        else:
            self.app_manager.save_recording(recording)
            self.app_manager.save_recording(skeleton_image_recording)

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

    def _is_recording_active(self):
        return self.app_manager.get_recording_status() in [RecordingState.RECORDING, RecordingState.COUNTING_DOWN]

    def review_sample(self, recording, skeleton_image_recording):
        sample_number = len(self.samples) + 1
        self.timer.stop()
        dialog = MovementPatternPreviewDialog(self.app_manager.skeleton_renderer, skeleton_image_recording,
                                             self.movement_name, self,
                                              question=f"Keep this recording as a valid sample?",
                                              accept_text="Keep sample", reject_text="Record again",
                                              title="Movement sample preview")
        accepted = dialog.exec()
        self.timer.start(1000 // self.fps)
        if not accepted:
            self.status_label.setText("Sample discarded.")
            return
        self.samples.append((recording, skeleton_image_recording))
        self.update_movement_info()
        if len(self.samples) >= self.sample_count:
            self.finish_session()
        else:
            self.status_label.setText(f"Sample {sample_number}/{self.sample_count} recorded."
                                      f"Press Rec to record the next one.")

    def finish_session(self):
        if not self.samples or self._is_recording_active():
            return
        try:
            saved_count = self.app_manager.save_movement_samples(self.samples)
        except OSError as error:
            QMessageBox.critical(self, "Cannot save movement samples", str(error))
            return
        QMessageBox.information(self, "Movement samples saved",
                                f"{saved_count} sample{saved_count > 0 : 's' ? ''} of movement '{self.movement_name}")
        self.samples = []
        self.app_manager.show_menu_window()

    def view_pattern(self):
        if self.pattern is None or self._is_recording_active():
            return
        try:
            pattern_recording = self.app_manager.load_movement_pattern_recording(self.pattern)
        except (OSError, ValueError, KeyError) as error:
            QMessageBox.critical(self, "Cannot load movement pattern", str(error))
            return
        self.timer.stop()
        dialog = MovementPatternPreviewDialog(self.app_manager.skeleton_renderer, pattern_recording,
                                             self.movement_name, self, question=None, accept_text=None,
                                              title="Movement pattern")
        dialog.exec()
        self.timer.start(1000 // self.fps)

    def go_to_menu_prompted(self):
        if self.action == RecordingAction.RECREATE and self.samples:
            answer = QMessageBox.question(
                self, "Unsaved samples",
                f"{len(self.samples)} sample{len(self.samples) > 0 : 's' ? ''} have not been saved. Save them before leaving?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save)
            if answer == QMessageBox.StandardButton.Cancel:
                return
            if answer == QMessageBox.StandardButton.Save:
                self.finish_session()
                return
            self.samples = []
        self.app_manager.show_menu_window()