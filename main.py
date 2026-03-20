import cv2
import numpy as np
from pykinect2 import PyKinectV2, PyKinectRuntime

kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Depth)

while True:
    if kinect.has_new_depth_frame():
        depth_frame = kinect.get_last_depth_frame()
        depth_frame = depth_frame.reshape((424, 512))
        depth_8bit = (depth_frame / 4500.0 * 255).clip(0, 255).astype(np.uint8)
        depth_color = cv2.applyColorMap(depth_8bit, cv2.COLORMAP_HOT)
        cv2.imshow('Depth Camera', depth_color)

    if cv2.waitKey(1):
        if 0xFF == ord('q'):
            break

kinect.close()
cv2.destroyAllWindows()
