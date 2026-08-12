import numpy as np


class MockPosition:
    x: float
    y: float
    z: float


class MockJoint:
    Position: MockPosition
    TrackingState: int

class MockBody:
    joints: dict
    is_tracked: bool = True

class MockBodyFrame:
    bodies: list

class MockColorFrame:
    frame: np.ndarray