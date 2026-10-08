from biometric.feature_extractor import FeatureExtractor
from movement.kinect_skeleton_model import KinectSkeletonModel


class BiometricSystem:
    def __init__(self, skeleton_model):
        self.feature_extractor = FeatureExtractor(skeleton_model)
    def normalize_joints_by_shoulder_distance(self, joints):
        self.feature_extractor.update_joints(joints)
        self.feature_extractor.normalize_joints_by_shoulder_distance()
    def calculate_angles(self, joints):
        self.feature_extractor.update_joints(joints)
        self.feature_extractor.calculate_angles()
    def get_angles(self):
        return self.feature_extractor.get_angles()
    def get_joint_cords_normalized(self):
        return self.feature_extractor.get_joint_cords_normalized()
