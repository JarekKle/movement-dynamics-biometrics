import math

import cv2

from movement.kinect_bones import KinectBones
from sources.iskeleton_renderer import ISkeletonRenderer


class KinectSkeletonRenderer(ISkeletonRenderer):
    def render(self, frame, joints):
        if frame is None:
            return None
        if joints is None:
            return frame
        rendered_frame = frame.reshape((1080, 1920, 4))
        rendered_frame = cv2.cvtColor(
            rendered_frame,
            cv2.COLOR_BGRA2BGR
        )

        rendered_frame = rendered_frame.copy()

        bones = KinectBones.get_bones()

        rendered_frame = self._draw_joints(
            rendered_frame,
            joints
        )

        rendered_frame = self._draw_bones(
            rendered_frame,
            joints,
            bones
        )

        return rendered_frame

    def _draw_joints(self, frame, joints):

        # rysowanie punktów
        for joint in joints:
            px, py = joint.x, joint.y

            if not math.isfinite(px) or not math.isfinite(py):
                continue

            x = int(px)
            y = int(py)

            cv2.circle(frame, (x, y), 6, (0, 255, 0), -1)

        return frame

    def _draw_bones(self, frame, joints, bones):
        for j1, j2 in bones:

            p1 = joints.get(j1)
            p2 = joints.get(j2)

            if p1 is None or p2 is None:
                continue

            px1, py1, _ = p1
            px2, py2, _ = p2
            if not math.isfinite(px1) or not math.isfinite(py1):
                continue
            if not math.isfinite(px2) or not math.isfinite(py2):
                continue
            x1 = int(px1)
            y1 = int(py1)
            x2 = int(px2)
            y2 = int(py2)

            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        return frame