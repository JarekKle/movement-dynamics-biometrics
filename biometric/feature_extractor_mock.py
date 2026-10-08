import math

import numpy as np

from movement.iskeleton_model import ISkeletonModel


class FeatureExtractorMock:
    def __init__(self, skeleton_model: ISkeletonModel):
        self.model = skeleton_model
        self._joint_cords = {}
        self._joint_cords_normalized = {}
        self._angles = {}

    def normalize_joints_by_shoulder_distance(self):
        spine_base = self._joint_cords[self.model.get_joint("spine_base")]
        shoulder_left = self._joint_cords[self.model.get_joint("shoulder_left")]
        shoulder_right = self._joint_cords[self.model.get_joint("shoulder_right")]
        if spine_base is None or shoulder_left is None or shoulder_right is None:
            return None

        width = np.linalg.norm(shoulder_right - shoulder_left)
        if width == 0:
            return
        normalized = {}

        for j, pos in self._joint_cords.items():
            normalized[j] = (pos - spine_base) / width

        return normalized

    def angle_3d(self, a: [float,float,float], b: [float,float,float], c: [float,float,float]) -> float:
        ba = np.array(a) - np.array(b)
        bc = np.array(c) - np.array(b)

        dot = np.dot(ba, bc)
        norm = np.linalg.norm(ba) * np.linalg.norm(bc)

        if norm == 0:
            return 0.0

        cos_angle = np.clip(dot / norm, -1.0, 1.0)
        angle = math.degrees(math.acos(cos_angle))
        return angle

    def joint_in_range(self, joint, x, y, z, x_range, y_range, z_range):

        self.normalize_joints_by_shoulder_distance()

        joint_xyz = self._joint_cords_normalized.get(joint)

        if joint_xyz is None:
            return False

        target = np.array([x, y, z])
        margin = np.array([x_range, y_range, z_range])

        diff = np.abs(joint_xyz - target)

        return np.all(diff <= margin)

    def joint_xyz(self, joint):
        return np.array([
            joint[0],
            joint[1],
            joint[2]
        ])

    def is_joint_tracked(self, joint):
        return joint
        pass
    def update_angles(self):
        if self._joint_cords_normalized is not None:
            joints = self._joint_cords_normalized
        elif self._joint_cords is not None:
            joints = self._joint_cords
        else:
            return None

        for angle in self.model.get_angles():
            j1, j2, j3 = angle.value
            if (
                    self.is_joint_tracked(joints[j1]) is None or
                    joints[j2] is None or
                    joints[j3] is None
            ):
                continue
            p1 = self.joint_xyz(joints[j1])
            p2 = self.joint_xyz(joints[j2])
            p3 = self.joint_xyz(joints[j3])
            ang = self.angle_3d(p1, p2, p3)
            self._angles[angle] = ang
