from PyQt6.QtWidgets import QDialog, QLineEdit, QComboBox, QSpinBox, QLabel, QFormLayout, QDialogButtonBox, QVBoxLayout

from application.app_config import MIN_SAMPLES_PER_SESSION, MAX_SAMPLES_PER_SESSION


class SampleRegistrationForm(QDialog):
    def __init__(self, patterns, default_sample_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record movement samples")
        self.patterns = list(patterns)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g. John Doe")
        self.pattern_input = QComboBox()
        for pattern in self.patterns:
            self.pattern_input.addItem(pattern.movement_name)

        self.sample_count_input = QSpinBox()
        self.sample_count_input.setRange(MIN_SAMPLES_PER_SESSION, MAX_SAMPLES_PER_SESSION)
        self.sample_count_input.setValue(
            min(max(default_sample_count, MIN_SAMPLES_PER_SESSION), MAX_SAMPLES_PER_SESSION))

        self.pattern_info = QLabel()
        self.pattern_info.setObjectName("statusLabel")
        self.pattern_info.setWordWrap(True)

        form = QFormLayout()
        form.addRow("Username", self.username_input)
        form.addRow("Movement pattern", self.pattern_input)
        form.addRow("", self.pattern_info)
        form.addRow("Number of samples", self.sample_count_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.button_box)

        self.username_input.textChanged.connect(self._update_state)
        self.pattern_input.currentIndexChanged.connect(self._update_state)
        self._update_state()

    def _update_state(self):
        pattern = self.get_pattern()
        if pattern is not None:
            self.pattern_info.setText(f"{len(pattern.joints)} joints, {pattern.frame_count} frames,"
                                      f" registered {pattern.registered_at}")
        else:
            self.pattern_info.setText("")
        accept_btn = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        accept_btn.setEnabled(bool(self.get_username()) and pattern is not None)

    def get_username(self):
        return self.username_input.text().strip()

    def get_pattern(self):
        index = self.pattern_input.currentIndex()
        if index >= 0 and index < len(self.patterns):
            return self.patterns[index]
        return None

    def get_sample_count(self):
        return self.sample_count_input.value()