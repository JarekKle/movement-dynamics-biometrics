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
    def render_body_frame(self,frame):
        if frame is None:
            return None
        rendered_frame = frame.reshape((1080, 1920, 4))
        rendered_frame = cv2.cvtColor(
            rendered_frame,
            cv2.COLOR_BGRA2BGR
        )

        return rendered_frame.copy()
    def render_skeleton(self, frame, joints2d, joint_selection_map=None):
        if frame is None:
            return None
        if joints2d is None:
            return frame
        bones = KinectBones.get_bones()
        rendered_frame = self._draw_joints(frame,joints2d, joint_selection_map)
        rendered_frame = self._draw_bones(rendered_frame,joints2d,bones, joint_selection_map)
        return rendered_frame
    def render(self, frame, joints2d, joint_selection_map=None):
        rendered_frame = self.render_body_frame(frame)

        return self.render_skeleton(rendered_frame, joints2d, joint_selection_map)
    def render_on_black_frame(self, joints2d, joint_selection_map=None, width=1920, height=1080):
        rendered_frame = self.create_empty_frame(width,height)
        return self.render_skeleton(rendered_frame, joints2d, joint_selection_map)

    def _draw_joints(self, frame, joints, joint_selection_map=None):
        try:
            for i in range(len(joints)):
                if joint_selection_map:
                    if not joint_selection_map[i]:
                        continue
                joint = joints[i]
                px, py = joint.x, joint.y

                if not math.isfinite(px) or not math.isfinite(py):
                    continue

                cv2.circle(
                    frame,
                    (int(px), int(py)),
                    6,
                    (0, 255, 0),
                    -1
                )
        except:
            for joint, pos in joints.items():
                if joint_selection_map:
                    if not joint_selection_map[i]:
                        continue
                px, py = pos.x, pos.y

                if not math.isfinite(px) or not math.isfinite(py):
                    continue

                cv2.circle(
                    frame,
                    (int(px), int(py)),
                    6,
                    (0, 255, 0),
                    -1
                )

        return frame

    def _draw_bones(self, frame, joints, bones, joint_selection_map=None):
            for j1, j2 in bones:
                if joint_selection_map:
                    if not joint_selection_map[j1] or not joint_selection_map[j2]:
                        continue
                try:
                    p1 = joints[j1]
                    p2 = joints[j2]
                except:
                        p1 = joints.get(j1, None)
                        p2 = joints.get(j2, None)
                if p1 is None or p2 is None:
                    continue
                px1, py1 = p1.x, p1.y
                px2, py2 = p2.x, p2.y

                if not all(map(math.isfinite, (px1, py1, px2, py2))):
                    continue

                cv2.line(
                    frame,
                    (int(px1), int(py1)),
                    (int(px2), int(py2)),
                    (0, 0, 255),
                    3
                )
            return frame

    def set_allow_inferred(self, allow_inferred):
        self._allow_inferred = allow_inferred