import math

import cv2
import numpy as np

from domain.movement.kinect.kinect_bones import KinectBones
from sources.iskeleton_renderer import ISkeletonRenderer


class KinectSkeletonRenderer(ISkeletonRenderer):
    def __init__(self, allow_inferred: bool):
        self._allow_inferred = allow_inferred

    def configure(self, allow_inferred):
        self._allow_inferred = allow_inferred
    def is_joint_tracked(self, joint):
        return joint[1] == 2
    def is_joint_inferred(self, joint):
        return joint[1] == 1
    def is_joint_not_tracked(self, joint):
        return joint[0] == 0
    def is_joint_allowed(self, joint):
        if self._allow_inferred:
            return self.is_joint_inferred(joint) or self.is_joint_tracked(joint)
        else:
            return self.is_joint_tracked(joint)

    def create_empty_frame(self, width=1920,height=1080):
        return np.zeros((height,width, 3),dtype=np.uint8)
    def render_body_frame(self,frame, target_size=None):
        if frame is None:
            return None
        rendered_frame = frame.reshape((1080, 1920, 4))
        if target_size is None or tuple(target_size) == (1920, 1080):
            return rendered_frame.copy()
        return cv2.resize(rendered_frame, tuple(target_size), interpolation=cv2.INTER_AREA)
    def render_skeleton(self, frame, joints2d, joint_selection_map=None):
        if frame is None:
            return None
        if joints2d is None:
            return frame
        bones = KinectBones.get_bones()
        scale = frame.shape[1] / 1920
        rendered_frame = self._draw_bones(frame,joints2d,bones, joint_selection_map, scale)
        rendered_frame = self._draw_joints(rendered_frame,joints2d, joint_selection_map, scale)
        return rendered_frame
    def render(self, frame, joints2d, joint_selection_map=None, target_size=None):
        rendered_frame = self.render_body_frame(frame, target_size)

        return self.render_skeleton(rendered_frame, joints2d, joint_selection_map)
    def render_on_black_frame(self, joints2d, joint_selection_map=None, width=1920, height=1080):
        rendered_frame = self.create_empty_frame(width,height)
        return self.render_skeleton(rendered_frame, joints2d, joint_selection_map)

    @staticmethod
    def _iter_joints(joints):
        if isinstance(joints, dict):
            return joints.items()
        return enumerate(joints)

    @staticmethod
    def _get_joint(joints, joint):
        if isinstance(joints, dict):
            return joints.get(joint)
        return joints[joint]

    @staticmethod
    def _color_for(frame, bgr):
        if frame.ndim == 3 and frame.shape[2] == 4:
            return (*bgr, 255)
        return bgr

    def _draw_joints(self, frame, joints, joint_selection_map=None, scale=1.0):
        color = self._color_for(frame, (0, 255, 0))
        for joint, point in self._iter_joints(joints):
            if joint_selection_map and not joint_selection_map.get(joint, False):
                continue
            px, py = point.x, point.y

            if not math.isfinite(px) or not math.isfinite(py):
                continue
            cv2.circle(
                frame,
                (int(px * scale), int(py * scale)),
                6,
                color,
                -1
            )
        return frame

    def _draw_bones(self, frame, joints, bones, joint_selection_map=None, scale=1.0):
        color = self._color_for(frame, (0, 0, 255))
        for j1, j2 in bones:
            if joint_selection_map:
                if not joint_selection_map.get(j1, False) or not joint_selection_map.get(j2, False):
                    continue
            p1 = self._get_joint(joints, j1)
            p2 = self._get_joint(joints, j2)
            if p1 is None or p2 is None:
                continue

            px1, py1 = p1.x, p1.y
            px2, py2 = p2.x, p2.y
            if not all(map(math.isfinite, (p1.x, p1.y, p2.x, p2.y))):
                continue
            cv2.line(
                frame,
                (int(px1 * scale), int(py1 * scale)),
                (int(px2 * scale), int(py2 * scale)),
                color,
                3
            )
        return frame

    def set_allow_inferred(self, allow_inferred):
        self._allow_inferred = allow_inferred