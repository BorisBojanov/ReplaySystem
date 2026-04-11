"""
Create a circular buffer in memory

Create an array (queue) of fixed size (n). 
When the buffer is full, the next incoming frame automatically overwrites the oldest frame.

The fixed size array allocates a fixed amount of RAM (e.g., 1GB to 4GB) to hold these frames.

Save the buffer as fragmented MP4 or MKV. These formats prevent file corruption if the system crashes or the buffer is interrupted.

Use efficient codecs like H.264 (broad compatibility) or HEVC (better quality per bitrate).

1. The active buffer must stay in system RAM. Only dump the contents to disk when a "Save" hotkey is pressed.



Secondary Goal:
    Use Hardware Encoding: Utilize NVENC (NVIDIA), AMF (AMD), or QuickSync (Intel) to encode video, which keeps CPU usage low.

"""

import cv2 as cv
import time

captureDevice = cv.VideoCapture(0)  # Open the default camera (index 0)
