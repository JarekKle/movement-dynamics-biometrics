from __future__ import annotations

import math

import cv2
from pykinect2 import PyKinectRuntime, PyKinectV2

from movement.kinect_angles import KinectAngles
from movement.kinect_bones import KinectBones
from movement.kinect_joints import KinectJoints
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
        self._joint_cords_normalized = {}
        self._angles = {}
        # koniec
        self._last_body_frame = None
        self._last_color_frame = None
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


    def configure(self, **kwargs):
        if "frame_types" in kwargs:
            self.frame_types = kwargs["frame_types"]
    def open(self):
        if self._running:
            return
        self._kinect = PyKinectRuntime.PyKinectRuntime(
            self.frame_types
        )
        self._running = True


    def close(self):
        if self._kinect:
            self._kinect.close()
            self._kinect = None
        self._running = False

    def is_opened(self) -> bool:
        return self._kinect is not None

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
        self.read_color()
        self.read_body()

    def joint_xyz(self, joint):
        return np.array([
            joint.Position.x,
            joint.Position.y,
            joint.Position.z
        ])

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

    def update_joint_cords(self):
        if not self.is_opened() or not self.is_running():
            return
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
                    self._joint_cords[joint] = self.joint_xyz(joints[joint])

    def get_joint_cords(self):
        return self._joint_cords

    def get_joint_cords_normalized(self):
        return self._joint_cords_normalized

    # do usunięcia
    def angle_3d(self, a, b, c):
        ba = np.array(a) - np.array(b)
        bc = np.array(c) - np.array(b)

        dot = np.dot(ba, bc)
        norm = np.linalg.norm(ba) * np.linalg.norm(bc)

        if norm == 0:
            return 0.0

        cos_angle = np.clip(dot / norm, -1.0, 1.0)
        angle = math.degrees(math.acos(cos_angle))
        return angle

    # do usunięcia
    def joint_in_range(self, joint, x, y, z, x_range, y_range, z_range):

        self.update_joint_cords()
        self.normalize_joints_by_shoulder_distance()

        joint_xyz = self._joint_cords_normalized.get(joint)

        if joint_xyz is None:
            return False

        target = np.array([x, y, z])
        margin = np.array([x_range, y_range, z_range])

        diff = np.abs(joint_xyz - target)

        return np.all(diff <= margin)

    #  do usunięcia
    def update_angles(self):
        if not self.is_opened() or not self.is_running():
            return None
        if self._last_body_frame is not None:
            for i in range(self._kinect.max_body_count):

                body = self._last_body_frame.bodies[i]

                if not body.is_tracked:
                    continue
                joints = body.joints
                for angle in KinectAngles:
                    j1, j2, j3 = angle.value
                    if (
                            joints[j1].TrackingState == PyKinectV2.TrackingState_NotTracked or
                            joints[j2].TrackingState == PyKinectV2.TrackingState_NotTracked or
                            joints[j3].TrackingState == PyKinectV2.TrackingState_NotTracked
                    ):
                        continue
                    p1 = self.joint_xyz(joints[j1])
                    p2 = self.joint_xyz(joints[j2])
                    p3 = self.joint_xyz(joints[j3])
                    ang = self.angle_3d(p1, p2, p3)
                    self._angles[angle] = ang

    def get_angles(self):
        return self._angles

