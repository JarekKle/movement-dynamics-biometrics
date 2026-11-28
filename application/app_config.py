import json
from dataclasses import dataclass, field, fields, asdict

MIN_FPS = 5
MAX_FPS = 30

MIN_SAMPLES_PER_SESSION = 1
MAX_SAMPLES_PER_SESSION = 10


@dataclass
class SourceConfig:
    source: str = "KINECT"
    allow_inferred: bool = True
    dynamic_tracking: bool = True


@dataclass
class DisplayConfig:
    fps: int = 30


@dataclass
class RecordingConfig:
    directory: str = "recordings"
    sample_rate: float = 15.0
    countdown_seconds: int = 5
    movement_activity_detection: bool = True
    still_movement_duration_threshold: float = 2.0
    joint_movement_threshold: float = 0.1
    active_joint_ratio_threshold: float = 0.1
    max_missing_seconds: float = 0.5
    min_recording_seconds: float = 1.0
    result_display_seconds: float = 5.0
    samples_per_session: int = 3


@dataclass
class AppConfig:
    source_config: SourceConfig = field(default_factory=SourceConfig)
    display_config: DisplayConfig = field(default_factory=DisplayConfig)
    recording_config: RecordingConfig = field(default_factory=RecordingConfig)
    joint_selection_map: dict = field(default_factory=dict)

    def validate_settings(self) -> list[str]:
        errors = []
        # FPS and sample rate range
        if self.display_config.fps > MAX_FPS or self.display_config.fps < MIN_FPS:
            errors.append(f"FPS must be between {MIN_FPS} and {MAX_FPS}.")
        if self.recording_config.sample_rate > self.display_config.fps:
            errors.append(f"Sample rate greater than FPS limit " +
                          f"({self.recording_config.sample_rate}>{self.display_config.fps}).")
        if self.recording_config.still_movement_duration_threshold * self.recording_config.sample_rate < 1:
            errors.append("Still movement shorter than one sample. " +
                          "Increase still movement duration threshold or sample rate.")
        if not self.recording_config.directory:
            errors.append("No recording directory found. Enter directory path.")
        if not MIN_SAMPLES_PER_SESSION <= self.recording_config.samples_per_session <= MAX_SAMPLES_PER_SESSION:
            errors.append(f"Samples per session must be between {MIN_SAMPLES_PER_SESSION} and {MAX_SAMPLES_PER_SESSION}")

        return errors


def _known_parameters(cls, parameters: dict) -> dict:
    names = {fld.name for fld in fields(cls)}
    known_params = {}
    for key, value in parameters.items():
        if key in names:
            known_params[key] = value
    return known_params


class ConfigRepository:
    def __init__(self, path="config.json"):
        self.path = path

    def load(self) -> AppConfig:
        try:
            with open(self.path, "r") as f:
                raw_config = json.load(f)
            config = AppConfig(
                source_config=SourceConfig(**_known_parameters(SourceConfig,
                                           raw_config.get("source_config", {}))),
                display_config=DisplayConfig(**_known_parameters(DisplayConfig,
                                                                 raw_config.get("display_config", {}))),
                recording_config=RecordingConfig(**_known_parameters(RecordingConfig,
                                                                     raw_config.get("recording_config", {}))),
                joint_selection_map=raw_config.get("joint_selection_map", {})
            )
        except (OSError, json.JSONDecodeError, TypeError):
            return AppConfig()
        if len(config.validate_settings())==0:
            return config
        else:
            return AppConfig()

    def save(self, config: AppConfig):
        with open(self.path, "w") as f:
            json.dump(asdict(config), f, indent=2)
            