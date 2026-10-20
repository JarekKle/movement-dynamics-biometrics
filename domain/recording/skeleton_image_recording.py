from dataclasses import dataclass

from domain.recording.skeleton_frame import SkeletonFrame
@dataclass
class SkeletonImageRecording:
    recording_id: str
    sample_rate: float
    frames: list
    metadata: dict