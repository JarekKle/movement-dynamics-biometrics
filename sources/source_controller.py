from Sources.isource import ISource
from Sources.kinect_source import KinectSource


class SourceController:
    def __init__(self, source: ISource):
        self.fps = None
        self.source = source

    def set_source(self, source: ISource):
        self.source = source
