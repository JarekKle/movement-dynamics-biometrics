import math
import sys

import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication

from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime

from movement.kinect_bones import KinectBones
from movement.kinect_joints import KinectJoints
from sources.kinect_source import KinectSource
from windows.app_manager import AppManager

def start_kinect():
    kinect = KinectSource()
    kinect.open()

def start_window():
    app = QApplication(sys.argv)
    window = AppManager()
    window.show()
    window.showMaximized()
    app.exec()
if __name__ == "__main__":
    start_window()