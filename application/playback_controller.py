import json
import os

import cv2
import numpy as np

from application.json_recording_repository import JsonRecordingRepository
from sources.kinect.kinect_skeleton_renderer import KinectSkeletonRenderer


class PlaybackController:
    def __init__(self, recording_repository, skeleton_renderer):
        self.recording_repository = recording_repository
        self.skeleton_renderer = skeleton_renderer
        # self._file_name = file_name or None
        self.skeleton_recording = None
        self.width = 1920
        self.height = 1080
    # def set_file(self, file_name):
    #     self._file_name = file_name
    # def is_file_exist(self):
    #     if self._file_name is None:
    #         return False
    #     return os.path.exists(self._file_name)
    # def is_file_image_file(self, data=None):
    #     if not self.is_file_exist():
    #         return False
    #     if self.skeleton_recording is None:
    #         try:
    #             return data["metadata"]["image"]
    #         except:
    #             return False
    #     else:
    #         try:
    #             return self.skeleton_recording["metadata"]["image"]
    #         except:
    #             return False
    def load_recording(self, recording_id):
        self.skeleton_recording = (
            self.recording_repository.load_skeleton_recording(recording_id)
        )

        return self.skeleton_recording
    def render_frame(self, frame_number):
        if self.skeleton_recording is None:
            return None

        skeleton_frame = self.skeleton_recording.frames[frame_number]

        return self.skeleton_renderer.render_on_black_frame(
            skeleton_frame.joints
        )
if __name__ == "__main__":
    repository = JsonRecordingRepository("../recordings")
    renderer = KinectSkeletonRenderer(True)
    playback_controller = PlaybackController(repository,renderer)

    recording = playback_controller.load_recording(
        "1f960dbf-e1e1-4844-a678-7c3fbfcfb0dbimage"
    )
    for i in range(len(recording.frames)):
        frame = playback_controller.render_frame(i)
        image = cv2.cvtColor(np.asarray(frame), cv2.COLOR_BGR2GRAY)
        cv2.imshow("OpenCV image",image)
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()