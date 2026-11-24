import json
import os
from dataclasses import asdict, fields

from domain.recording.movement_pattern import MovementPattern


class MovementPatternRepository:
    INDEX_FILE_NAME = "movement_patterns.json"

    def __init__(self, directory: str):
        self.directory = directory

    def set_directory(self, directory):
        self.directory = directory

    def get_index_path(self):
        return os.path.join(self.directory, self.INDEX_FILE_NAME)

    def load_patterns(self) -> list[MovementPattern]:
        path = self.get_index_path()
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
            known = {fld.name for fld in fields(MovementPattern)}
            return [
                MovementPattern(**{key: value for key, value in raw_pattern.items() if key in known})
                for raw_pattern in raw_data.get("patterns", [])
            ]
        except (OSError, json.JSONDecodeError, TypeError, AttributeError) as error:
            raise ValueError(f"Movement pattern index {path} cannot be read: {error}") from error

    def save_patterns(self, patterns: list[MovementPattern]):
        os.makedirs(self.directory, exist_ok=True)
        path = self.get_index_path()
        temp_path = path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump({"patterns": [asdict(pattern) for pattern in patterns]}, file, indent=2, ensure_ascii=False)
        os.replace(temp_path, path)  # the index is never left half-written

    def add_pattern(self, pattern: MovementPattern):
        patterns = self.load_patterns()
        if self._find(patterns, pattern.movement_name) is not None:
            raise ValueError(f"Movement pattern '{pattern.movement_name}' is already registered.")
        patterns.append(pattern)
        self.save_patterns(patterns)

    def contains(self, movement_name) -> bool:
        return self._find(self.load_patterns(), movement_name) is not None

    def get_pattern_count(self) -> int:
        return len(self.load_patterns())

    def get_pattern_names(self) -> list[str]:
        return [pattern.movement_name for pattern in self.load_patterns()]

    @staticmethod
    def _find(patterns, movement_name):
        wanted = movement_name.strip().casefold()
        for pattern in patterns:
            if pattern.movement_name.strip().casefold() == wanted:
                return pattern
        return None
