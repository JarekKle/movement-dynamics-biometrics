
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
        return [e for e in KinectJoints]