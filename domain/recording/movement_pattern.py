from dataclasses import field, dataclass


@dataclass
class MovementPattern:
    movement_name: str
    recording_file: str
    image_recording_file: str
    joints: list = field(default_factory=list)
    sample_rate: float = 0.0
    frame_count: int = 0
    registered_at: str = ""
