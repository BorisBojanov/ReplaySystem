import cv2
"""How I want it to work:

cv2.VideoCapture(index) tries to open a camera device at the given index.
cap.isOpened() returns True if the camera is accessible.
max_index=10 means it checks /dev/video0 to /dev/video9 on Linux or camera 0–9 on Windows/macOS.

"""

def list_available_cameras(max_index=10):
    available_cameras = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap is not None and cap.isOpened():
            print(f"Camera found at index {index}")
            available_cameras.append(index)
            cap.release()
        else:
            print(f"No camera at index {index}")
    return available_cameras

# Run the scanner
camera_indexes = list_available_cameras()
print("Available camera indexes:", camera_indexes)