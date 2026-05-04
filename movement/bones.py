from Movement.joint_name import JointName

class Bones:

    SPINE = [
        (JointName.HEAD, JointName.NECK),
        (JointName.NECK, JointName.SPINE_SHOULDER),
        (JointName.SPINE_SHOULDER, JointName.SPINE_MID),
        (JointName.SPINE_MID, JointName.SPINE_BASE),
    ]

    LEFT_ARM = [
        (JointName.SPINE_SHOULDER, JointName.SHOULDER_LEFT),
        (JointName.SHOULDER_LEFT, JointName.ELBOW_LEFT),
        (JointName.ELBOW_LEFT, JointName.WRIST_LEFT),
        (JointName.WRIST_LEFT, JointName.HAND_LEFT),
        (JointName.HAND_LEFT, JointName.HAND_TIP_LEFT),
        (JointName.WRIST_LEFT, JointName.THUMB_LEFT),
    ]

    RIGHT_ARM = [
        (JointName.SPINE_SHOULDER, JointName.SHOULDER_RIGHT),
        (JointName.SHOULDER_RIGHT, JointName.ELBOW_RIGHT),
        (JointName.ELBOW_RIGHT, JointName.WRIST_RIGHT),
        (JointName.WRIST_RIGHT, JointName.HAND_RIGHT),
        (JointName.HAND_RIGHT, JointName.HAND_TIP_RIGHT),
        (JointName.WRIST_RIGHT, JointName.THUMB_RIGHT),
    ]

    LEFT_LEG = [
        (JointName.SPINE_BASE, JointName.HIP_LEFT),
        (JointName.HIP_LEFT, JointName.KNEE_LEFT),
        (JointName.KNEE_LEFT, JointName.ANKLE_LEFT),
        (JointName.ANKLE_LEFT, JointName.FOOT_LEFT),
    ]

    RIGHT_LEG = [
        (JointName.SPINE_BASE, JointName.HIP_RIGHT),
        (JointName.HIP_RIGHT, JointName.KNEE_RIGHT),
        (JointName.KNEE_RIGHT, JointName.ANKLE_RIGHT),
        (JointName.ANKLE_RIGHT, JointName.FOOT_RIGHT),
    ]

    ALL = SPINE + LEFT_ARM + RIGHT_ARM + LEFT_LEG + RIGHT_LEG

    @staticmethod
    def get_bones():
        return Bones.ALL