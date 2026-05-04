from movement.kinect_angles import KinectAngles
from movement.kinect_bones import KinectBones
from movement.iskeleton_model import ISkeletonModel
from movement.kinect_joints import KinectJoints


class KinectSkeletonModel(ISkeletonModel):
    def get_joints(self):
        return KinectJoints.get_joints()

    def get_bones(self):
        return KinectBones.get_bones()

    def get_angles(self):
        return KinectAngles.get_angles()