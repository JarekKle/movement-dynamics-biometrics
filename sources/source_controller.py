from sources.iskeleton_renderer import ISkeletonRenderer
from sources.isource import ISource
from sources.kinect_source import KinectSource


class SourceController:
    def __init__(self, source: ISource, skeleton_renderer: ISkeletonRenderer):
        self._joints = None
        self._body = None
        self._frame = None
        self.fps = None
        self.source = source
        self.skeleton_renderer = skeleton_renderer

    def set_source(self, source: ISource):
        self.source = source

    def get_new_frame(self):
        self.source.update()
        self._frame = self.source.get_color_frame()
        self._body = self.source.get_body_frame()
        self._joints = self.source.joints_2d()

    def get_display_frame(self):
        self.get_new_frame()
        return self._frame
        frame = self.skeleton_renderer.render(
            frame=self._frame,
            joints=self._joints
        )
        return frame


    def update_frame(self):
        if self.source.is_opened() and self.source.is_running():
            new_frame = self.get_display_frame()
            return new_frame