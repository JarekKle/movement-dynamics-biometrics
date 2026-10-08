import math
import random
import sys

import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication

from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime

from biometric.feature_extractor_mock import FeatureExtractorMock
from generators.mock_frames_generator import MockFramesGenerator
from movement.kinect_bones import KinectBones
from movement.kinect_joints import KinectJoints
from movement.kinect_skeleton_model import KinectSkeletonModel
from sources.kinect_source import KinectSource
from sources.sources import Sources
from windows.app_manager import AppManager


def start_kinect():
    kinect = KinectSource()
    kinect.open()


def tracefunc(frame, event, arg, indent=[0]):
    if event == "call":
        indent[0] += 2
        print("-" * indent[0] + "> call function", frame.f_code.co_name)
    elif event == "return":
        print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
        indent[0] -= 2
    return tracefunc


import sys

# sys.setprofile(tracefunc)
def start_window():
    app = QApplication(sys.argv)
    window = AppManager(Sources.KINECT)
    window.show()
    window.showMaximized()
    app.exec()


def test_feature_extractor():
    model = KinectSkeletonModel()
    generator = MockFramesGenerator(model)
    feature_extractor = FeatureExtractorMock(model)
    frames = generator.generate_mock_frames(5)
    FeatureExtractorMock._joint_cords = frames[0]
    print(feature_extractor.normalize_joints_by_shoulder_distance())

if __name__ == "__main__":
    # test_feature_extractor()
    start_window()