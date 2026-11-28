from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np


class ISource(ABC):

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def configure(self, **kwargs):
        pass
    @abstractmethod
    def stop(self):
        pass
    @abstractmethod
    def start(self):
        pass
    @abstractmethod
    def close(self):
        pass
    @abstractmethod
    def is_opened(self) -> bool:
        pass
    @abstractmethod
    def is_available(self):
        pass
    @abstractmethod
    def is_running(self):
        pass
    @abstractmethod
    def read_body(self):
        pass
    @abstractmethod
    def read_color(self):
        pass
    @abstractmethod
    def get_color_frame(self):
        pass
    @abstractmethod
    def get_body_frame(self):
        pass
    @abstractmethod
    def update(self):
        pass
    @abstractmethod
    def joint_xyz(self):
        pass
    @abstractmethod
    def count_tracked_bodies(self):
        pass
    @abstractmethod
    def get_joints_raw(self):
        pass
    @abstractmethod
    def joints_2d(self):
        pass
    @abstractmethod
    def get_joint_cords(self):
        pass