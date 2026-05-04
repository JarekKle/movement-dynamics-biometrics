from abc import ABC, abstractmethod


class ISkeletonModel(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_joints(self):
        pass

    @abstractmethod
    def get_bones(self):
        pass

    @abstractmethod
    def get_angles(self):
        pass