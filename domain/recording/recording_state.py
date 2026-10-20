from enum import Enum


class RecordingState(Enum):
    NOT_RECORDING = 1,
    COUNTING_DOWN = 2,
    RECORDING = 3,
    FINISHED_RECORDING = 4,
    CANCELLED_RECORDING = 5