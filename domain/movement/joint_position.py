from dataclasses import dataclass


@dataclass
class JointPosition:
    x: float
    y: float
    z: float
    tracking_state: int