from dataclasses import dataclass
from typing import Mapping

from domain.movement.joint_position import JointPosition
from domain.movement.kinect.kinect_joints import KinectJoints


@dataclass
class SkeletonFrame:
    frame_number: int
    timestamp: float
    joints: Mapping[KinectJoints, JointPosition]