from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from domain.movement.kinect.joint_2d import Joint2D


class SkeletonPlaybackPlayer(QObject):
    frame_ready = pyqtSignal(object)  # np.ndarray (BGR)

    def __init__(self, skeleton_renderer, fps=30, loop_pause_seconds=1.0, parent=None):
        super().__init__(parent)
        self.skeleton_renderer = skeleton_renderer
        self.fps = fps
        self.loop_pause_seconds = loop_pause_seconds
        self._frames = []
        self._sample_rate = 1.0
        self._time = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)

    def load(self, image_recording):
        frames = [self._to_joint_dict(frame) for frame in image_recording.frames]
        self._frames = [frame for frame in frames if frame]
        self._sample_rate = image_recording.sample_rate or 1.0
        self._time = 0.0

    def has_frames(self):
        return len(self._frames) > 0

    def get_duration(self):
        return max(0.0, (len(self._frames) - 1) / self._sample_rate)

    def play(self):
        if self.has_frames():
            self._time = 0.0
            self._emit_frame()
            self._timer.start(1000 // self.fps)

    def stop(self):
        self._timer.stop()

    def _on_tick(self):
        self._time += 1.0 / self.fps
        if self._time > self.get_duration() + self.loop_pause_seconds:
            self._time = 0.0
        self._emit_frame()

    def _emit_frame(self):
        position = min(self._time, self.get_duration()) * self._sample_rate
        index = int(position)
        ratio = position - index
        frame_from = self._frames[index]
        frame_to = self._frames[min(index + 1, len(self._frames) - 1)]
        joints = {}
        for joint, point in frame_from.items():
            next_point = frame_to.get(joint, point)
            joints[joint] = Joint2D(
                joint,
                point.x + (next_point.x - point.x) * ratio,
                point.y + (next_point.y - point.y) * ratio
            )
        self.frame_ready.emit(self.skeleton_renderer.render_on_black_frame(joints))

    @staticmethod
    def _to_joint_dict(frame):
        if hasattr(frame, "joints"):
            return {int(joint): point for joint, point in frame.joints.items()}
        return {int(point.joint): point for point in frame}
