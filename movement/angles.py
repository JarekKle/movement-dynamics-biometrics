from enum import Enum
from Movement.joint_name import JointName


class Angles(Enum):
    LEFT_ARM_ELBOW = (JointName.SHOULDER_LEFT,
         JointName.ELBOW_LEFT,
         JointName.WRIST_LEFT)


    RIGHT_ARM_ELBOW = (JointName.SHOULDER_RIGHT,
         JointName.ELBOW_RIGHT,
         JointName.WRIST_RIGHT)


    LEFT_ARM_SHOULDER = (JointName.NECK,
         JointName.SHOULDER_LEFT,
         JointName.ELBOW_LEFT)


    RIGHT_ARM_SHOULDER = (JointName.NECK,
         JointName.SHOULDER_RIGHT,
         JointName.ELBOW_RIGHT)


    LEFT_LEG_KNEE = (JointName.HIP_LEFT,
         JointName.KNEE_LEFT,
         JointName.ANKLE_LEFT)

    RIGHT_LEG_KNEE = (JointName.HIP_RIGHT,
         JointName.KNEE_RIGHT,
         JointName.ANKLE_RIGHT)

    LEFT_LEG_HIP = (JointName.SPINE_BASE,
         JointName.HIP_LEFT,
         JointName.KNEE_LEFT)

    RIGHT_LEG_HIP =  (JointName.SPINE_BASE,
         JointName.HIP_RIGHT,
         JointName.KNEE_RIGHT)
    SPINE_LEFT = (JointName.SHOULDER_LEFT,
         JointName.SPINE_SHOULDER,
         JointName.SPINE_MID)
    SPINE_RIGHT = (JointName.SHOULDER_RIGHT,
         JointName.SPINE_SHOULDER,
         JointName.SPINE_MID)

    POSTURE_SPINE = (JointName.NECK,
         JointName.SPINE_SHOULDER,
         JointName.SPINE_MID)
    @staticmethod
    def get_angles():
        return [e for e in JointName]