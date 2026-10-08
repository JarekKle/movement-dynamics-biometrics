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
            "spine_mid": KinectJoints.SPINE_MID,
            "neck": KinectJoints.NECK,
            "head": KinectJoints.HEAD,
            "spine_shoulder": KinectJoints.SPINE_SHOULDER,
            "elbow_left": KinectJoints.ELBOW_LEFT,
            "wrist_left": KinectJoints.WRIST_LEFT,
            "hand_left": KinectJoints.HAND_LEFT,
            "hand_tip_left": KinectJoints.HAND_TIP_LEFT,
            "thumb_left": KinectJoints.THUMB_LEFT,
            "elbow_right": KinectJoints.ELBOW_RIGHT,
            "wrist_right": KinectJoints.WRIST_RIGHT,
            "hand_right": KinectJoints.HAND_RIGHT,
            "hand_tip_right": KinectJoints.HAND_TIP_RIGHT,
            "thumb_right": KinectJoints.THUMB_RIGHT,
            "hip_left": KinectJoints.HIP_LEFT,
            "knee_left": KinectJoints.KNEE_LEFT,
            "ankle_left": KinectJoints.ANKLE_LEFT,
            "foot_left": KinectJoints.FOOT_LEFT,
            "hip_right": KinectJoints.HIP_RIGHT,
            "knee_right": KinectJoints.KNEE_RIGHT,
            "ankle_right": KinectJoints.ANKLE_RIGHT,
            "foot_right": KinectJoints.FOOT_RIGHT
        }
        self._joint_names_map = {value: name for name, value in self._joint_map.items()}
    def get_joints(self):
        return KinectJoints.get_joints()

    def get_joint_names(self):
        return self._joint_map.keys()

    def get_joint(self, name: str):
        return self._joint_map.get(name)

    def get_bones(self):
        return KinectBones.get_bones()

    def get_angles(self):
        return KinectAngles.get_angles()
