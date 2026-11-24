import json
import os
from dataclasses import asdict

from domain.movement.joint_position import JointPosition
from domain.movement.kinect.kinect_joints import KinectJoints
from domain.recording.skeleton_frame import SkeletonFrame
from domain.recording.skeleton_recording import SkeletonRecording


class JsonRecordingRepository:
    def __init__(self, directory: str):
        self.directory = directory

    def set_directory(self, directory):
        os.makedirs(directory, exist_ok=True)
        self.directory = directory
    def save(self, recording):
        os.makedirs(self.directory, exist_ok=True)
        path = f"{self.directory}/{recording.recording_id}.json"
        with open(path, "w") as file:
            json.dump(
                asdict(recording),
                file,
                indent=2
            )

    def load_skeleton_recording(self, recording_id):
        path = os.path.join(
            self.directory,
            f"{recording_id}.json"
        )

        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as file:
            raw_data = json.load(file)

        return self._deserialize_recording(raw_data)

    def _deserialize_recording(self, raw_data):
        skeleton_recording = SkeletonRecording(
            recording_id=raw_data["recording_id"],
            sample_rate=raw_data["sample_rate"],
            frames=[],
            metadata=raw_data["metadata"]
        )
        for i, frame in enumerate(raw_data["frames"]):
            skeleton_frame = self._deserialize_frame(frame, i, skeleton_recording.sample_rate)
            skeleton_recording.frames.append(skeleton_frame)
        return skeleton_recording

    def _deserialize_frame(self, frame, frame_number, sample_rate):
        skeleton_frame = SkeletonFrame(
            frame_number=frame_number,
            timestamp=frame_number / sample_rate,
            joints={KinectJoints(joint_data["joint"]): JointPosition(
                x=joint_data["x"],
                y=joint_data["y"],
                z=0,
                tracking_state=2
            ) for joint_data in frame}
        )
        return skeleton_frame
