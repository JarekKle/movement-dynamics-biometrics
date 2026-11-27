from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt

from ui.camera_label import CameraLabel
from ui.skeleton_playbak_player import SkeletonPlaybackPlayer


class MovementPatternPreviewDialog(QDialog):
    def __init__(self, skeleton_renderer, skeleton_image_recording, movement_name, parent=None,
                 question="Register this recording as a new movement pattern?",
                 accept_text="Register pattern", reject_text="Discard", title="Movement pattern preview"):
        super().__init__(parent)
        self.setWindowTitle("Movement pattern preview")
        self.setMinimumSize(640, 480)

        self.player = SkeletonPlaybackPlayer(skeleton_renderer, parent=self)
        self.player.load(skeleton_image_recording)

        title_label = QLabel(f"Movement: {movement_name}")
        title_label.setObjectName("movementNameLabel")

        self.image_label = CameraLabel()
        self.image_label.setObjectName("cameraView")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(480, 270)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.player.frame_ready.connect(self.image_label.update_frame)

        if self.player.has_frames():
            info_text = (f"Duration: {self.player.get_duration():.1f} s · "
                         f"{len(skeleton_image_recording.frames)} samples. ")
            if question:
                info_text += f" {question}"
        else:
            info_text = "The recording contains no skeleton data and cannot be registered."
            self.image_label.setText("No data")
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)

        self.button_box = QDialogButtonBox()
        if accept_text is not None:
            self.btn_register = self.button_box.addButton(accept_text, QDialogButtonBox.ButtonRole.AcceptRole)
            self.button_box.addButton(reject_text, QDialogButtonBox.ButtonRole.RejectRole)
            self.btn_register.setEnabled(self.player.has_frames())
        else:
            self.btn_register = None
            self.button_box.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(self.image_label, stretch=1)
        layout.addWidget(info_label)
        layout.addWidget(self.button_box)

    def showEvent(self, event):
        super().showEvent(event)
        self.player.play()

    def done(self, result):
        self.player.stop()
        super().done(result)
