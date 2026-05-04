
from movement.kinect_joints import KinectJoints

class KinectBones:

    SPINE = [
        (KinectJoints.HEAD, KinectJoints.NECK),
        (KinectJoints.NECK, KinectJoints.SPINE_SHOULDER),
        (KinectJoints.SPINE_SHOULDER, KinectJoints.SPINE_MID),
        (KinectJoints.SPINE_MID, KinectJoints.SPINE_BASE),
    ]

    LEFT_ARM = [
        (KinectJoints.SPINE_SHOULDER, KinectJoints.SHOULDER_LEFT),
        (KinectJoints.SHOULDER_LEFT, KinectJoints.ELBOW_LEFT),
        (KinectJoints.ELBOW_LEFT, KinectJoints.WRIST_LEFT),
        (KinectJoints.WRIST_LEFT, KinectJoints.HAND_LEFT),
        (KinectJoints.HAND_LEFT, KinectJoints.HAND_TIP_LEFT),
        (KinectJoints.WRIST_LEFT, KinectJoints.THUMB_LEFT),
    ]

    RIGHT_ARM = [
        (KinectJoints.SPINE_SHOULDER, KinectJoints.SHOULDER_RIGHT),
        (KinectJoints.SHOULDER_RIGHT, KinectJoints.ELBOW_RIGHT),
        (KinectJoints.ELBOW_RIGHT, KinectJoints.WRIST_RIGHT),
        (KinectJoints.WRIST_RIGHT, KinectJoints.HAND_RIGHT),
        (KinectJoints.HAND_RIGHT, KinectJoints.HAND_TIP_RIGHT),
        (KinectJoints.WRIST_RIGHT, KinectJoints.THUMB_RIGHT),
    ]

    LEFT_LEG = [
        (KinectJoints.SPINE_BASE, KinectJoints.HIP_LEFT),
        (KinectJoints.HIP_LEFT, KinectJoints.KNEE_LEFT),
        (KinectJoints.KNEE_LEFT, KinectJoints.ANKLE_LEFT),
        (KinectJoints.ANKLE_LEFT, KinectJoints.FOOT_LEFT),
    ]

    RIGHT_LEG = [
        (KinectJoints.SPINE_BASE, KinectJoints.HIP_RIGHT),
        (KinectJoints.HIP_RIGHT, KinectJoints.KNEE_RIGHT),
        (KinectJoints.KNEE_RIGHT, KinectJoints.ANKLE_RIGHT),
        (KinectJoints.ANKLE_RIGHT, KinectJoints.FOOT_RIGHT),
    ]

    ALL = SPINE + LEFT_ARM + RIGHT_ARM + LEFT_LEG + RIGHT_LEG

    @staticmethod
    def get_bones():
        return KinectBones.ALL