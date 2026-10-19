import json
from dataclasses import asdict


class JsonRecordingRepository:
    def __init__(self, directory: str):
        self.directory = directory
    def save(self, recording):
        path = f"{self.directory}/{recording.recording_id}.json"
        with open(path, "w") as file:
            json.dump(
                asdict(recording),
                file,
                indent=2
            )