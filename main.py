from PyQt6.QtWidgets import QApplication

from biometric.feature_extractor_mock import FeatureExtractorMock
from generators.mock_frames_generator import MockFramesGenerator
from domain.movement.kinect.kinect_skeleton_model import KinectSkeletonModel
from sources.kinect.kinect_source import KinectSource
from sources.source_registry import SourceRegistry
from application.app_manager import AppManager


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
    window = AppManager(SourceRegistry.KINECT, "C:\\Users\\user\\Desktop\\movement-dynamics-biometrics\\recordings")
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