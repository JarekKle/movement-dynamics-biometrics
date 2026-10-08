
from movement.kinect_joints import KinectJoints


class KinectAngles:
    LEFT_ARM_ELBOW = (KinectJoints.SHOULDER_LEFT,
                      KinectJoints.ELBOW_LEFT,
                      KinectJoints.WRIST_LEFT)


    RIGHT_ARM_ELBOW = (KinectJoints.SHOULDER_RIGHT,
                       KinectJoints.ELBOW_RIGHT,
                       KinectJoints.WRIST_RIGHT)


    LEFT_ARM_SHOULDER = (KinectJoints.NECK,
                         KinectJoints.SHOULDER_LEFT,
                         KinectJoints.ELBOW_LEFT)


    RIGHT_ARM_SHOULDER = (KinectJoints.NECK,
                          KinectJoints.SHOULDER_RIGHT,
                          KinectJoints.ELBOW_RIGHT)


    LEFT_LEG_KNEE = (KinectJoints.HIP_LEFT,
                     KinectJoints.KNEE_LEFT,
                     KinectJoints.ANKLE_LEFT)

    RIGHT_LEG_KNEE = (KinectJoints.HIP_RIGHT,
                      KinectJoints.KNEE_RIGHT,
                      KinectJoints.ANKLE_RIGHT)

    LEFT_LEG_HIP = (KinectJoints.SPINE_BASE,
                    KinectJoints.HIP_LEFT,
                    KinectJoints.KNEE_LEFT)

    RIGHT_LEG_HIP =  (KinectJoints.SPINE_BASE,
                      KinectJoints.HIP_RIGHT,
                      KinectJoints.KNEE_RIGHT)
    SPINE_LEFT = (KinectJoints.SHOULDER_LEFT,
                  KinectJoints.SPINE_SHOULDER,
                  KinectJoints.SPINE_MID)
    SPINE_RIGHT = (KinectJoints.SHOULDER_RIGHT,
                   KinectJoints.SPINE_SHOULDER,
                   KinectJoints.SPINE_MID)

    POSTURE_SPINE = (KinectJoints.NECK,
                     KinectJoints.SPINE_SHOULDER,
                     KinectJoints.SPINE_MID)


    @staticmethod
    def get_angles():
        return {
            "LEFT_ARM_ELBOW": KinectAngles.LEFT_ARM_ELBOW,
            "RIGHT_ARM_ELBOW": KinectAngles.RIGHT_ARM_ELBOW,
            "LEFT_ARM_SHOULDER": KinectAngles.LEFT_ARM_SHOULDER,
            "RIGHT_ARM_SHOULDER": KinectAngles.RIGHT_ARM_SHOULDER,
            "LEFT_LEG_KNEE": KinectAngles.LEFT_LEG_KNEE,
            "RIGHT_LEG_KNEE": KinectAngles.RIGHT_LEG_KNEE,
            "LEFT_LEG_HIP": KinectAngles.LEFT_LEG_HIP,
            "RIGHT_LEG_HIP": KinectAngles.RIGHT_LEG_HIP,
            "SPINE_LEFT": KinectAngles.SPINE_LEFT,
            "SPINE_RIGHT": KinectAngles.SPINE_RIGHT,
            "POSTURE_SPINE": KinectAngles.POSTURE_SPINE
        }