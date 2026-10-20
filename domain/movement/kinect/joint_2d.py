from dataclasses import dataclass


@dataclass
class Joint2D:
    joint: int
    x: float
    y: float