import random


class MockFramesGenerator:
    def __init__(self, model):
        self._model = model

    def generate_mock_frames(self, number_of_frames=10):
        frames = {}
        positions = {}
        for name in self._model.get_joint_names():
            positions[name] = {
                "x": random.uniform(-1.5, 1.5),
                "y": random.uniform(-2.3, 1.2),
                "z": random.uniform(-1.7, 1.2)

            }
        for i_frame in range(number_of_frames):
            frame = {}

            for name, position in positions.items():
                position["x"] += random.uniform(-0.02, 0.02)
                position["y"] += random.uniform(-0.02, 0.02)
                position["z"] += random.uniform(-0.02, 0.02)

                frame[name] = {
                    "x": position["x"],
                    "y": position["y"],
                    "z": position["z"]
                }

            frames[i_frame] = frame

        return frames
