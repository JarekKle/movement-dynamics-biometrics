from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QCheckBox, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt

class KinectJointSelectionDialog(QDialog):

    def __init__(self, joint_translation_map, joint_selection_map, bones_translation_map):
        self.joint_translation_map = joint_translation_map
        self.joint_selection_map = joint_selection_map
        self.bones_translation_map = bones_translation_map
        self.bone_joints_map = {}
        for bone_name, bone_parts in self.bones_translation_map.items():
            joints = set()
            for bone_part in bone_parts:
                for joint in bone_part:
                    joints.add(joint)
            self.bone_joints_map[bone_name] = joints
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
            check_box = QCheckBox(self.canvas)
            check_box.move(move_x, move_y)
            check_box.setChecked(is_checked)
            check_box.setStyleSheet(
                "QCheckBox { color: red;}"
            )
            check_box.stateChanged.connect(
                lambda checked, value=joint_value:
                    self.on_joint_toggled(value, checked)
            )
            check_box.adjustSize()
            check_box.raise_()
            self.joint_checkboxes[joint_name] = check_box

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        bones_widget = QWidget()
        self.bones_layout = QVBoxLayout(bones_widget)
        self.bones_checkboxes = {}
        for bone_name, bone_value in bones_translation_map.items():
            check_box = QCheckBox(bone_name)
            self.bones_checkboxes[bone_name] = check_box
            check_box.stateChanged.connect(
                lambda checked, value=bone_name:
                    self.on_bone_toggled(value, checked)
            )
            self.bones_layout.addWidget(check_box)
        self.update_bone_checkboxes()
        self.bones_layout.addStretch()
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.canvas)
        content_layout.addWidget(bones_widget)

        layout = QVBoxLayout()
        layout.addLayout(content_layout)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def on_joint_toggled(self, joint_value, checked):
        self.joint_selection_map[joint_value] = (checked > 0)

        self.update_bone_checkboxes()
    # TODO add bone toggled function
    def update_bone_checkboxes(self):
        for bone_name, joints in self.bone_joints_map.items():
            is_checked = True
            for joint in joints:
                if not self.joint_selection_map[joint]:
                    is_checked = False
            bone_checkbox = self.bones_checkboxes[bone_name]
            bone_checkbox.blockSignals(True)
            bone_checkbox.setChecked(is_checked)
            bone_checkbox.blockSignals(False)
    def on_bone_toggled(self, bone_name, checked):
        is_checked = (checked > 0)
        joints = self.bone_joints_map[bone_name]
        for joint_name, joint in self.joint_translation_map.items():
            if joint not in joints:
                continue
            self.joint_selection_map[joint_name] = is_checked

            joint_checkbox = self.joint_checkboxes[joint_name]

            joint_checkbox.blockSignals(True)
            joint_checkbox.setChecked(is_checked)
            joint_checkbox.blockSignals(False)

    def get_joint_selection_map(self):
        joint_selection_map = {}
        for joint_name, checkbox in self.joint_checkboxes.items():
            joint_value = self.joint_translation_map[joint_name]
            joint_selection_map[joint_value] = checkbox.isChecked()
        self.joint_selection_map = joint_selection_map
        return self.joint_selection_map

