from PyQt6.QtWidgets import QWidget, QCheckBox, QSpinBox, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, \
    QDoubleSpinBox, QVBoxLayout, QGroupBox, QFileDialog, QMessageBox

from application.app_config import MIN_FPS, MAX_FPS, AppConfig, SourceConfig, DisplayConfig, RecordingConfig, \
    MIN_SAMPLES_PER_SESSION, MAX_SAMPLES_PER_SESSION


class DoubleInput(QDoubleSpinBox):
    def __init__(self, minimum, maximum, step, precision, unit=""):
        super().__init__()
        self.setRange(minimum, maximum)
        self.setSingleStep(step)
        self.setDecimals(precision)
        self.setSuffix(unit)
class ConfigWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        # Source
        self.allow_inferred = QCheckBox()
        self.dynamic_tracking = QCheckBox()
        source = QFormLayout()
        source.addRow("Allow inferred joints (assumed positions)",
                      self.allow_inferred)
        source.addRow("Enable dynamic tracking (draw skeleton, constantly check positions)",
                      self.dynamic_tracking)

        # Display
        self.fps = QSpinBox()
        self.fps.setRange(MIN_FPS, MAX_FPS)
        display = QFormLayout()
        display.addRow("Set display FPS", self.fps)

        # Recording
        self.directory = QLineEdit()
        browse_dir = QPushButton("Search")
        browse_dir.clicked.connect(self.choose_directory)
        dir_row = QHBoxLayout()
        dir_row.addWidget(self.directory)
        dir_row.addWidget(browse_dir)

        self.sample_rate = DoubleInput(1, 30, 1, 1, " Hz")
        self.countdown_seconds = QSpinBox()
        self.countdown_seconds.setRange(0, 15)
        self.countdown_seconds.setSuffix(" s")

        self.movement_activity_detection = QCheckBox()
        self.still_movement_duration_threshold = DoubleInput(0.5, 10, 0.1, 1, " s")
        self.joint_movement_threshold = DoubleInput(0.01, 1.0, 0.01, 2, " m")
        self.active_joint_ratio_threshold = DoubleInput(0.01, 1.0, 0.01, 2)
        self.max_missing_seconds = DoubleInput(0.0, 1.0, 0.1, 1, " s")
        self.min_recording_seconds = DoubleInput(1.0, 30.0, 0.5, 1, " s")
        self.result_display_seconds = DoubleInput(0.5, 30.0, 0.5, 1, " s")
        self.samples_per_session = QSpinBox()
        self.samples_per_session.setRange(MIN_SAMPLES_PER_SESSION, MAX_SAMPLES_PER_SESSION)

        recording = QFormLayout()
        recording.addRow("Recording directory", dir_row)
        recording.addRow("Sample rate", self.sample_rate)
        recording.addRow("Countdown before recording", self.countdown_seconds)
        recording.addRow("Stop recording if the user stops moving", self.movement_activity_detection)
        recording.addRow("Stillness duration before recording is stopped", self.still_movement_duration_threshold)
        recording.addRow("Joint movement threshold", self.joint_movement_threshold)
        recording.addRow("Active joint ratio (how many joints must be moving to not stop recording)",
                         self.active_joint_ratio_threshold)
        recording.addRow("Time a user could be missing before recording is stopped", self.max_missing_seconds)
        recording.addRow("Minimum recording length", self.min_recording_seconds)
        recording.addRow("Result message duration", self.result_display_seconds)
        recording.addRow("Default number of samples recorded in one session", self.samples_per_session)

        self.movement_activity_detection.toggled.connect(self._update_enabled)

        # Buttons
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save)
        btn_defaults = QPushButton("Restore defaults")
        btn_defaults.clicked.connect(lambda: self.load_values(AppConfig()))
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self.app_manager.show_menu_window)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons_list = [btn_save, btn_defaults, btn_back]
        for button in buttons_list:
            buttons.addWidget(button)

        layout = QVBoxLayout(self)
        names = {
            "Source": source,
            "Display": display,
            "Recording": recording
        }
        for title, form in names.items():
            box = QGroupBox(title)
            box.setLayout(form)
            layout.addWidget(box)
        layout.addStretch()
        layout.addLayout(buttons)
    def save(self):
        config = self.read_input_values()
        errors = config.validate_settings()
        if errors:
            QMessageBox.warning(self, "Invalid configuration", "\n".join(errors))
            return
        try:
            self.app_manager.apply_config(config)
        except OSError as e:
            QMessageBox.critical(self, "Cannot save configuration", str(e))
            return
        self.app_manager.show_menu_window()
    def load_values(self, app_config: AppConfig):
        self.allow_inferred.setChecked(app_config.source_config.allow_inferred)
        self.dynamic_tracking.setChecked(app_config.source_config.dynamic_tracking)
        self.fps.setValue(app_config.display_config.fps)
        rec = app_config.recording_config
        self.directory.setText(rec.directory)
        self.sample_rate.setValue(rec.sample_rate)
        self.countdown_seconds.setValue(rec.countdown_seconds)
        self.movement_activity_detection.setChecked(rec.movement_activity_detection)
        self.still_movement_duration_threshold.setValue(rec.still_movement_duration_threshold)
        self.joint_movement_threshold.setValue(rec.joint_movement_threshold)
        self.active_joint_ratio_threshold.setValue(rec.active_joint_ratio_threshold)
        self.max_missing_seconds.setValue(rec.max_missing_seconds)
        self.min_recording_seconds.setValue(rec.min_recording_seconds)
        self.result_display_seconds.setValue(rec.result_display_seconds)
        self.samples_per_session.setValue(rec.samples_per_session)
        self._update_enabled()
    def _update_enabled(self):
        is_enabled = self.movement_activity_detection.isChecked()
        stillness_related = [self.still_movement_duration_threshold, self.joint_movement_threshold, self.active_joint_ratio_threshold]
        for field in stillness_related:
            field.setEnabled(is_enabled)

    def choose_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Recording directory", self.directory.text())
        if path:
            self.directory.setText(path)

    def read_input_values(self) -> AppConfig:
        curr_config = self.app_manager.config
        new_app_config = AppConfig(
            source_config=SourceConfig(
                source=curr_config.source_config.source,
                allow_inferred=self.allow_inferred.isChecked(),
                dynamic_tracking=self.dynamic_tracking.isChecked()
            ),
            display_config=DisplayConfig(
                fps=self.fps.value()
            ),
            recording_config=RecordingConfig(
                directory=self.directory.text().strip(),
                sample_rate=self.sample_rate.value(),
                countdown_seconds=self.countdown_seconds.value(),
                movement_activity_detection=self.movement_activity_detection.isChecked(),
                still_movement_duration_threshold=self.still_movement_duration_threshold.value(),
                joint_movement_threshold=self.joint_movement_threshold.value(),
                active_joint_ratio_threshold=self.active_joint_ratio_threshold.value(),
                max_missing_seconds=self.max_missing_seconds.value(),
                min_recording_seconds=self.min_recording_seconds.value(),
                result_display_seconds=self.result_display_seconds.value(),
                samples_per_session=self.samples_per_session.value()
            ),
        joint_selection_map=dict(curr_config.joint_selection_map)
        )
        return new_app_config

