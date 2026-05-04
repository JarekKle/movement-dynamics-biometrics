import numpy as np

from movement.iskeleton_model import ISkeletonModel


class FeatureExtractor:
    def __init__(self, skeleton_model: ISkeletonModel):
        self.model = skeleton_model

    def normalize_joints_by_shoulder_distance(self, joints):
        spine_base = joints[self.model.get_joint("spine_base")]
        shoulder_left = joints[self.model.get_joint("shoulder_left")]
        shoulder_right = joints[self.model.get_joint("shoulder_right")]
        if spine_base is None or shoulder_left is None or shoulder_right is None:
            return None

        width = np.linalg.norm(shoulder_right - shoulder_left)
        if width == 0:
            return
        normalized = {}

        for j, pos in joints.items():
            normalized[j] = (pos - spine_base) / width

        return normalized