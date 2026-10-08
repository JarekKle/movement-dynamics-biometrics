import math

import numpy as np

from movement.iskeleton_model import ISkeletonModel


class FeatureExtractor:
    def __init__(self, skeleton_model: ISkeletonModel):
        self.model = skeleton_model
        self._joint_cords = {}
        self._joint_cords_normalized = {}
        self._angles = {}
        self._allow_inferred = False
    def get_joint_cords_normalized(self):
        return self._joint_cords_normalized
    def update_joints(self, joints):
        self._joint_cords = joints

    # def normalize_joints_by_shoulder_distance(self):
    #     if self._joint_cords is None:
    #         return None
    #     spine_base = self._joint_cords[self.model.get_joint("spine_base")]
    #     spine_base = np.array([spine_base.x, spine_base.y])
    #     shoulder_left = self._joint_cords[self.model.get_joint("shoulder_left")]
    #     shoulder_left = np.array([shoulder_left.x, shoulder_left.y])
    #     shoulder_right = self._joint_cords[self.model.get_joint("shoulder_right")]
    #     shoulder_right = np.array([shoulder_right.x, shoulder_right.y])
    #     if spine_base is None or shoulder_left is None or shoulder_right is None:
    #         return None
    #
    #     width = np.linalg.norm(shoulder_right - shoulder_left)
    #     if width == 0:
    #         return
    #     normalized = {}
    #
    #     for j, joint in enumerate(self._joint_cords):
    #         pos = np.array([joint.x, joint.y])
    #         normalized[j] = (pos - spine_base) / width
    #
    #     return normalized
    def is_joint_tracked(self, joint):
        return joint[1] == 2
    def is_joint_inferred(self, joint):
        return joint[1] == 1
    def is_joint_not_tracked(self, joint):
        return joint[0] == 0
    def is_joint_allowed(self, joint):
        if self._allow_inferred:
            return self.is_joint_inferred(joint) or self.is_joint_tracked(joint)
        else:
            return self.is_joint_tracked(joint)
    def normalize_joints_by_shoulder_distance(self):
        if len(self._joint_cords) == 0:
            return None
        spine_base = self.joint_xyz(self._joint_cords[self.model.get_joint("spine_base")]) # joint has structure [[x, y, z], tracked_state]
        shoulder_left = self.joint_xyz(self._joint_cords[self.model.get_joint("shoulder_left")])
        shoulder_right = self.joint_xyz(self._joint_cords[self.model.get_joint("shoulder_right")])
        if spine_base is None or shoulder_left is None or shoulder_right is None:
            return None

        width = np.linalg.norm(shoulder_right - shoulder_left)
        if width == 0:
            return
        normalized = {}

        for j, pos in self._joint_cords.items():
            if self.is_joint_allowed(pos):

                joint_pos = self.joint_xyz(pos)
                normalized[j] = (joint_pos - spine_base) / width

        self._joint_cords_normalized = normalized

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
        joint_coords = joint[0] # joint has structure [[x, y, z], tracking_state]
        return np.array([
            joint_coords[0],
            joint_coords[1],
            joint_coords[2]
        ])

        pass
    def calculate_angles(self):
        if len(self._joint_cords) == 0:
            return None
        angles = {}
        for angle, (j1, j2, j3) in self.model.get_angles().items():
            j1_cords = self._joint_cords[j1]
            j2_cords = self._joint_cords[j2]
            j3_cords = self._joint_cords[j3]

            if self.is_joint_allowed(j1_cords) and self.is_joint_allowed(j2_cords) and self.is_joint_allowed(j3_cords):
                p1 = self.joint_xyz(j1_cords)
                p2 = self.joint_xyz(j2_cords)
                p3 = self.joint_xyz(j3_cords)
                ang = self.angle_3d(p1, p2, p3)
            else:
                ang = "Untracked"
            angles[angle] = ang
        self._angles = angles
    def get_angles(self):
        return self._angles