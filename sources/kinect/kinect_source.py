from __future__ import annotations

from pykinect2 import PyKinectRuntime, PyKinectV2

from domain.movement.kinect.joint_2d import Joint2D
from domain.movement.kinect.kinect_joints import KinectJoints
from sources.isource import ISource
import numpy as np


class KinectSource(ISource):
    def __init__(self):
        self._running = False
        self._kinect: PyKinectRuntime.PyKinectRuntime() = None
        self.frame_types = (
                PyKinectV2.FrameSourceTypes_Color |
                PyKinectV2.FrameSourceTypes_Body
        )
        # do usunięcia
        self._joint_cords = {}
        self._last_body_frame = None
        self._last_color_frame = None
        self.joint_selection_map = None
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


    def configure(self, **kwargs):
        if "frame_types" in kwargs:
            self.frame_types = kwargs["frame_types"]

    def open(self):
        if self.is_opened():
            self.start()
            return
        self._kinect = PyKinectRuntime.PyKinectRuntime(self.frame_types)
        self.start()

    def close(self):
        if self.is_opened():
            self._kinect.close()
            self._kinect = None
        self._running = False

    def stop(self):
        if self.is_opened():
            self._running = False
    def start(self):
        if self.is_opened():
            self._running = True

    def is_opened(self) -> bool:
        return self._kinect is not None

    def is_available(self) -> bool:
        if self._kinect is None:
            return False
        try:
            return self._kinect._sensor.IsAvailable
        except Exception:
            return False
    def is_running(self) -> bool:
        return self._running

    def read_body(self):
        if not self.is_opened() or not self.is_running():
            return None
        if self._kinect.has_new_body_frame():
            self._last_body_frame = self._kinect.get_last_body_frame()
        return None

    def read_color(self):
        if not self.is_opened() or not self.is_running():
            return None
        if self._kinect.has_new_color_frame():
            self._last_color_frame = self._kinect.get_last_color_frame()
        return None


    def get_color_frame(self):
        return self._last_color_frame

    def get_body_frame(self):
        return self._last_body_frame

    def update(self):
        if not self.is_available():
            self._last_body_frame = None
            self._last_color_frame = None
            return
        self.read_color()
        self.read_body()

    def joint_xyz(self, joint):
        return np.array([
            joint.Position.x,
            joint.Position.y,
            joint.Position.z
        ])

    def count_tracked_bodies(self):
        if not self.is_opened() or not self.is_running():
            return None
        if self._last_body_frame is None:
            return 0
        body_count = 0
        for body in self._last_body_frame.bodies:
            if body.is_tracked:
                body_count += 1
        return body_count
    def get_joints_raw(self) -> dict:
        joint_cords_raw = {}
        if not self.is_opened() or not self.is_running():
            return None
        if self._last_body_frame is not None:
            for i in range(self._kinect.max_body_count):

                body = self._last_body_frame.bodies[i]

                if not body.is_tracked:
                    continue
                joints = body.joints

                for joint in KinectJoints.get_joints():
                    x = joints[joint].Position.x
                    y = joints[joint].Position.y
                    z = joints[joint].Position.z
                    tracked = joints[joint].TrackingState
                    joint_cords_raw[joint] = [self.joint_xyz(joints[joint]), tracked]
        return joint_cords_raw
    def joints_2d(self):
        body_frame = self._last_body_frame
        if body_frame is not None:
            for i in range(self._kinect.max_body_count):

                body = body_frame.bodies[i]

                if not body.is_tracked:
                    continue
                joints = body.joints
                joint_points = self._kinect.body_joints_to_color_space(joints)
                return joint_points

    def get_joint_cords(self):
        return self._joint_cords
