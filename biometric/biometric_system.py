from biometric.feature_extractor import FeatureExtractor
from movement.kinect_skeleton_model import KinectSkeletonModel


class BiometricSystem:
    def __init__(self):
        self.skeleton_model = KinectSkeletonModel()
        self.feature_extractor = FeatureExtractor(self.skeleton_model)
