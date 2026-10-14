from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QCheckBox, QWidget
from PyQt6.QtCore import Qt

class KinectJointSelectionDialog(QDialog):

    def __init__(self, joint_translation_map, joint_selection_map):
        self.joint_translation_map = joint_translation_map
        self.joint_selection_map = joint_selection_map
        self._joint_offset_map = {
            "Spine base": (200,343),
            "Left shoulder": (144,141),
            "Right shoulder": (256,141),
            "Middle of the spine": (200,233),
            "Neck": (200,104),
            "Head": (200,67),
            "Spine shoulder": (200,134),
            "Left elbow": (128,223),
            "Left wrist": (110,284),
            "Left hand": (98,306),
            "Left hand tip": (100,324),
            "Left thumb": (118,298),
            "Right elbow": (275,225),
            "Right wrist": (290,284),
            "Right hand": (302,308),
            "Right hand tip": (300,324),
            "Right thumb": (282,298),
            "Left hip": (153,366),
            "Left knee": (145,459),
            "Left ankle": (135,556),
            "Left foot": (109,569),
            "Right hip": (247,366),
            "Right knee": (256,459),
            "Right ankle": (264,556),
            "Right foot": (290,569)
        }
        self.offset = (-9,-7)
        super().__init__()

        self.setWindowTitle("Joint Selection!")
        self.canvas = QWidget()
        self.canvas.setFixedSize(400,600)

        self.image_label = QLabel(self.canvas)
        pixmap = QPixmap('assets/human.png').scaled(
            400, 600,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)
        self.image_label.setGeometry(0, 0, 400, 600)
        self.image_label.lower()


        self.joint_checkboxes = {}
        for joint_name, joint_value in joint_translation_map.items():
            is_checked = self.joint_selection_map[joint_value]
            move_x, move_y = self._joint_offset_map[joint_name]
            move_x = move_x + self.offset[0]
            move_y = move_y + self.offset[1]
            check_box = QCheckBox(joint_name, self.canvas)
            check_box.move(move_x, move_y)
            check_box.setChecked(is_checked)
            check_box.setStyleSheet(
                "QCheckBox { color: red;}"
            )
            check_box.adjustSize()
            check_box.raise_()
            self.joint_checkboxes[joint_name] = check_box

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel("Check joints that need to be registered")
        layout.addWidget(message)
        layout.addWidget(self.canvas)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
    def get_joint_selection_map(self):
        joint_selection_map = {}
        for name,checkbox in self.joint_checkboxes.items():
            joint_tag = self.joint_translation_map[name]
            joint_selection_map[joint_tag] = checkbox.isChecked()
        self.joint_selection_map = joint_selection_map
        return joint_selection_map