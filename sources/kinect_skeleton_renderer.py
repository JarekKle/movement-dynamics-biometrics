import math

import cv2

from movement.kinect_bones import KinectBones
from sources.iskeleton_renderer import ISkeletonRenderer


from movement.kinect_bones import KinectBones
from sources.iskeleton_renderer import ISkeletonRenderer


class KinectSkeletonRenderer(ISkeletonRenderer):
    def __init__(self, allow_inferred: bool):
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
    def render(self, frame, joints2d):
        if frame is None:
            return None
        rendered_frame = frame.reshape((1080, 1920, 4))
        rendered_frame = cv2.cvtColor(
            rendered_frame,
            cv2.COLOR_BGRA2BGR
        )

        rendered_frame = rendered_frame.copy()

        if joints2d is None:
            return rendered_frame
        bones = KinectBones.get_bones()
        rendered_frame = self._draw_joints(rendered_frame,joints2d)
        rendered_frame = self._draw_bones(rendered_frame,joints2d,bones)
        return rendered_frame

    def _draw_joints(self, frame, joints):
        for joint in joints:
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

        return frame

    def _draw_bones(self, frame, joints, bones):
        for j1, j2 in bones:
            p1 = joints[j1]
            p2 = joints[j2]
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