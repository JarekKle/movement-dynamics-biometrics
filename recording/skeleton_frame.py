from dataclasses import dataclass
from typing import Mapping

from movement.joint_position import JointPosition
from movement.kinect_joints import KinectJoints


@dataclass
class SkeletonFrame:
    frame_number: int
    timestamp: float
    joints: Mapping[KinectJoints, JointPosition]