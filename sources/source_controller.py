from sources.iskeleton_renderer import ISkeletonRenderer
from sources.isource import ISource
from sources.kinect_source import KinectSource
from sources.tracking_status import TrackingStatus


class SourceController:
    def __init__(self, source: ISource, skeleton_renderer: ISkeletonRenderer, dynamic_tracking: bool):
        self._joints2d = None
        self._joints_raw = None
        self._body = None
        self._frame = None
        self.fps = None
        self.tracking_status = TrackingStatus.SOURCE_DISCONNECTED
        self.source = source
        self.skeleton_renderer = skeleton_renderer
        self._dynamic_tracking = dynamic_tracking

    def set_source(self, source: ISource):
        self.source = source
    def is_dynamic_tracking_on(self):
        return self._dynamic_tracking
    def get_new_frame(self):
        self.source.update()
        self._frame = self.source.get_color_frame()
        self._body = self.source.get_body_frame()

    def get_joints_data(self):
        self._joints_raw = self.source.get_joints_raw()
        self._joints2d = self.source.joints_2d()
    def get_display_frame(self):
        self.get_new_frame()
        return self._frame
    def get_display_frame_with_skeleton(self):
        self.get_new_frame()
        self.get_joints_data()
        frame = self.skeleton_renderer.render(
            frame=self._frame,
            joints2d=self._joints2d
        )
        return frame

    def update_frame(self, dynamic_tracking: bool):
        if self.source.is_opened() and self.source.is_running():
            if dynamic_tracking:
                new_frame = self.get_display_frame_with_skeleton()
            else:
                new_frame = self.get_display_frame()
            return new_frame
    def get_joints_raw(self):
        return self._joints_raw

    def determine_tracking_status(self):
        if not self.source.is_opened():
            new_status = TrackingStatus.SOURCE_DISCONNECTED
        else:
            body_count = self.source.count_tracked_bodies()
            if body_count == 0:
                new_status = TrackingStatus.NO_PEOPLE_TRACKED
            if body_count > 1:
                new_status = TrackingStatus.TOO_MANY_PEOPLE_TRACKED
            if body_count == 1:
                if self.is_required_joints_tracked():
                    new_status = TrackingStatus.ALL_REQUIRED_JOINTS_TRACKED
                else:
                    new_status = TrackingStatus.REQUIRED_JOINTS_NOT_TRACKED
            if new_status == TrackingStatus.NO_PEOPLE_TRACKED and (self.tracking_status == TrackingStatus.REQUIRED_JOINTS_NOT_TRACKED or self.tracking_status == TrackingStatus.ALL_REQUIRED_JOINTS_TRACKED):
                new_status = TrackingStatus.PERSON_LOST
        self.tracking_status = new_status

    # TODO
    def is_required_joints_tracked(self):
        return True