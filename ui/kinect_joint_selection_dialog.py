from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QCheckBox, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt

class KinectJointSelectionDialog(QDialog):

    def __init__(self, joint_translation_map, joint_selection_map, segment_joints_map, parent=None):
        super().__init__(parent)
        self._selection = dict(joint_selection_map)
        self._segments = {}
        for name, joints in segment_joints_map.items():
            self._segments[name] = joints
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


        self._joint_checkboxes = {}
        for joint_name, joint_value in joint_translation_map.items():
            move_x, move_y = self._joint_offset_map[joint_name]
            move_x = move_x + self.offset[0]
            move_y = move_y + self.offset[1]
            check_box = QCheckBox(self.canvas)
            check_box.move(move_x, move_y)
            check_box.setToolTip(joint_name)
            check_box.setStyleSheet(
                "QCheckBox { color: red;}"
            )
            check_box.clicked.connect(lambda _checked=False, j=joint_value: self._toggle((j,)))
            check_box.adjustSize()
            check_box.raise_()
            self._joint_checkboxes[joint_value] = check_box

        segments_widget = QWidget()
        self.segments_layout = QVBoxLayout(segments_widget)
        self._segment_checkboxes = {}
        for segment_name, joints in self._segments.items():
            check_box = QCheckBox(segment_name)
            self._segment_checkboxes[segment_name] = check_box
            check_box.clicked.connect(lambda _checked=False, js=joints: self._toggle(js))  # segment
            self.segments_layout.addWidget(check_box)
        self.segments_layout.addStretch()

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.canvas)
        content_layout.addWidget(segments_widget)

        layout = QVBoxLayout()
        layout.addLayout(content_layout)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self._refresh()

    def _toggle(self, joints):
        new_value = not all(self._selection[joint] for joint in joints)
        for joint in joints:
            self._selection[joint] = new_value
        self._refresh()
    def _refresh(self):
        for joint, check_box in self._joint_checkboxes.items():
            check_box.setChecked(self._selection[joint])
        for segment_name, check_box in self._segment_checkboxes.items():
            states = []
            for joint_name in self._segments[segment_name]:
                states.append(self._selection[joint_name])
            if all(states):
                check_box.setCheckState(Qt.CheckState.Checked)
            elif any(states):
                check_box.setCheckState(Qt.CheckState.PartiallyChecked)
            else:
                check_box.setCheckState(Qt.CheckState.Unchecked)

    def get_joint_selection_map(self):
        return dict(self._selection)
