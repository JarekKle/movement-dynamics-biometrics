from movement.kinect_angles import KinectAngles
from movement.kinect_bones import KinectBones
from movement.iskeleton_model import ISkeletonModel
from movement.kinect_joints import KinectJoints


class KinectSkeletonModel(ISkeletonModel):
    def __init__(self):
        self._joint_map = {
            "spine_base": KinectJoints.SPINE_BASE,
            "shoulder_left": KinectJoints.SHOULDER_LEFT,
            "shoulder_right": KinectJoints.SHOULDER_RIGHT,
        }
    def get_joints(self):
        return KinectJoints.get_joints()

    def get_joint(self, name: str):
        return self._joint_map.get(name)

    def get_bones(self):
        return KinectBones.get_bones()

    def get_angles(self):
        return KinectAngles.get_angles()