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
        self._joint_cords = {}
        self._joint_cords_normalized = {}
        self._angles = {}
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


    def get_new_frame(self) -> np.ndarray:
        if not self.is_opened() or not self.is_running():
            return None

        bones = KinectBones.get_bones()
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.read_body()
        self.read_color()
        body_frame = self._last_body_frame
        color_frame = self._last_color_frame

        # COLOR FRAME
        if color_frame is not None:
            frame = color_frame.reshape((1080, 1920, 4))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)



        # BODY FRAME
        if body_frame is not None:
            self._last_body_frame = body_frame
            for i in range(self._kinect.max_body_count):

                body = body_frame.bodies[i]

                if not body.is_tracked:
                    continue

                joints = body.joints
                joint_points = self._kinect.body_joints_to_color_space(joints)


                # rysowanie punktów
                for j in range(PyKinectV2.JointType_Count):

                    px = joint_points[j].x
                    py = joint_points[j].y

                    if not math.isfinite(px) or not math.isfinite(py):
                        continue

                    x = int(px)
                    y = int(py)

                    cv2.circle(frame, (x, y), 6, (0, 255, 0), -1)

                # rysowanie kości
                for bone in bones:

                    j1, j2 = bone
                    px1 = joint_points[j1].x
                    py1 = joint_points[j1].y
                    px2 = joint_points[j2].x
                    py2 = joint_points[j2].y
                    if not math.isfinite(px1) or not math.isfinite(py1):
                        continue
                    if not math.isfinite(px2) or not math.isfinite(py2):
                        continue
                    x1 = int(px1)
                    y1 = int(py1)
                    x2 = int(px2)
                    y2 = int(py2)

                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

        frame = cv2.resize(frame, (1280, 720))
        return frame

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

    def normalize_joints_by_shoulder_distance(self, joints = None):
        if not self.is_opened() or not self.is_running():
            return
        base = self._joint_cords.get(KinectJoints.SPINE_BASE)
        shoulder_left = self._joint_cords.get(KinectJoints.SHOULDER_LEFT)
        shoulder_right = self._joint_cords.get(KinectJoints.SHOULDER_RIGHT)

        if base is None or shoulder_left is None or shoulder_right is None:
            return

        shoulder_width = np.linalg.norm(shoulder_right - shoulder_left)

        if shoulder_width == 0:
            return

        self._joint_cords_normalized.clear()

        if joints is not None:
            for joint_name in joints:
                joint_pos = self._joint_cords.get(joint_name)
                normalized_joint = (joint_pos - base) / shoulder_width
                self._joint_cords_normalized[joint_name] = normalized_joint
        else:
            for joint_name, joint_pos in self._joint_cords.items():
                normalized_joint = (joint_pos - base) / shoulder_width

                self._joint_cords_normalized[joint_name] = normalized_joint

    def get_joint_cords(self):
        return self._joint_cords

    def get_joint_cords_normalized(self):
        return self._joint_cords_normalized

    def joint_xyz(self, joint):
        return np.array([
            joint.Position.x,
            joint.Position.y,
            joint.Position.z
        ])

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
