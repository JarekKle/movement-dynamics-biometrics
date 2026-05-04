from enum import IntEnum
from pykinect2 import PyKinectV2


class JointName(IntEnum):
    SPINE_BASE = PyKinectV2.JointType_SpineBase
    SPINE_MID = PyKinectV2.JointType_SpineMid
    NECK = PyKinectV2.JointType_Neck
    HEAD = PyKinectV2.JointType_Head
    SPINE_SHOULDER = PyKinectV2.JointType_SpineShoulder

    SHOULDER_LEFT = PyKinectV2.JointType_ShoulderLeft
    ELBOW_LEFT = PyKinectV2.JointType_ElbowLeft
    WRIST_LEFT = PyKinectV2.JointType_WristLeft
    HAND_LEFT = PyKinectV2.JointType_HandLeft
    HAND_TIP_LEFT = PyKinectV2.JointType_HandTipLeft
    THUMB_LEFT = PyKinectV2.JointType_ThumbLeft

    SHOULDER_RIGHT = PyKinectV2.JointType_ShoulderRight
    ELBOW_RIGHT = PyKinectV2.JointType_ElbowRight
    WRIST_RIGHT = PyKinectV2.JointType_WristRight
    HAND_RIGHT = PyKinectV2.JointType_HandRight
    HAND_TIP_RIGHT = PyKinectV2.JointType_HandTipRight
    THUMB_RIGHT = PyKinectV2.JointType_ThumbRight

    HIP_LEFT = PyKinectV2.JointType_HipLeft
    KNEE_LEFT = PyKinectV2.JointType_KneeLeft
    ANKLE_LEFT = PyKinectV2.JointType_AnkleLeft
    FOOT_LEFT = PyKinectV2.JointType_FootLeft

    HIP_RIGHT = PyKinectV2.JointType_HipRight
    KNEE_RIGHT = PyKinectV2.JointType_KneeRight
    ANKLE_RIGHT = PyKinectV2.JointType_AnkleRight
    FOOT_RIGHT = PyKinectV2.JointType_FootRight

    @staticmethod
    def get_joints():
        return [e for e in JointName]