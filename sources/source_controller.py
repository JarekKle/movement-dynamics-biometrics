import time

from domain.movement.joint_position import JointPosition
from domain.recording.skeleton_frame import SkeletonFrame
from sources.iskeleton_renderer import ISkeletonRenderer
from sources.isource import ISource
from sources.tracking_status import TrackingStatus


class SourceController:
    def __init__(self, source: ISource, skeleton_renderer: ISkeletonRenderer, dynamic_tracking: bool, allow_inferred: bool, joint_selection_map):
        self._joints2d = None
        self._joints_raw = None
        self._body = None
        self._frame = None
        self.fps = None
        self.frame_number = 0
        self.tracking_status = TrackingStatus.SOURCE_DISCONNECTED
        self.source = source
        self.skeleton_renderer = skeleton_renderer
        self._dynamic_tracking = dynamic_tracking
        self._allow_inferred = allow_inferred
        self.joint_selection_map = joint_selection_map
    def set_source(self, source: ISource):
        self.source = source
    def is_dynamic_tracking_on(self):
        return self._dynamic_tracking
    def get_new_frame(self):
        self.source.update()
        self._frame = self.source.get_color_frame()
        self._body = self.source.get_body_frame()
        self.frame_number+=1

    def get_joints_data(self):
        self._joints_raw = self.source.get_joints_raw()
        self._joints2d = self.source.joints_2d()
    def get_joints_as_skeleton_frame(self):
        self._joints_raw = self.source.get_joints_raw()
        joint_positions = {}
        for joint_name, joint_cords in self._joints_raw.items():
            if self.joint_selection_map[joint_name]:
                if not self.is_joint_allowed(joint_cords):
                    return None

                joint_positions[joint_name.name] = JointPosition(
                    joint_cords[0][0],
                    joint_cords[0][1],
                    joint_cords[0][2],
                    joint_cords[1]
                )
        return SkeletonFrame(
            self.frame_number,
            time.time(),
            joint_positions
        )
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
        new_status = self.tracking_status
        if not self.source.is_opened():
            new_status = TrackingStatus.SOURCE_DISCONNECTED
        elif not self.source.is_running():
            new_status = TrackingStatus.SOURCE_PAUSED
        else:
            body_count = self.source.count_tracked_bodies()
            if body_count == 0:
                if self.tracking_status is not TrackingStatus.PERSON_LOST:
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
    def is_ready_to_record(self):
        return self.tracking_status==TrackingStatus.ALL_REQUIRED_JOINTS_TRACKED
    def get_tracking_status(self):
        return self.tracking_status
    def is_joint_tracked(self, joint):
        return joint[1] == 2
    def is_joint_inferred(self, joint):
        return joint[1] == 1
    def is_joint_not_tracked(self, joint):
        return joint[1] == 0
    def is_joint_allowed(self, joint):
        if self._allow_inferred:
            return self.is_joint_inferred(joint) or self.is_joint_tracked(joint)
        else:
            return self.is_joint_tracked(joint)
    def is_required_joints_tracked(self):
        for joint, position in self._joints_raw.items():
            if self.joint_selection_map[joint]:
                if not self.is_joint_allowed(position):
                    print(f"Missing joint: {joint.name}")
                    return False
        return True
    def set_joint_selection_map(self, joint_selection_map):
        self.joint_selection_map = joint_selection_map