# Video Replay System
# Libraries used: pip3.13 opencv-python numpy
import os
import numpy as np
import cv2
import collections
import time


###
# Continuous capture loop:
#	Use OpenCV to continuously capture frames.
#	Store frames in a deque (double-ended queue) with a max length = FPS * n_seconds.
# ###

# === Configuration ===
BUFFER_SECONDS = 5  # how many seconds of video to keep
OUTPUT_FILENAME = "replay_output.mp4"
TRIGGER_KEY = ord('s')  # press 's' to save replay
# === Initialize Capture ===
cap = cv2.VideoCapture(0)  # change to a file if needed

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30  # fallback to 30 if undetectable
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# Deque to store last N seconds of frames
buffer = collections.deque(maxlen=fps * BUFFER_SECONDS)

print(f"Recording... Press 's' to save last {BUFFER_SECONDS} seconds to file. Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Frame capture failed. Exiting.")
        break

    buffer.append(frame)

    # Display preview
    cv2.imshow('Live Feed', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == TRIGGER_KEY:
        print("Saving replay...")
        out = cv2.VideoWriter(OUTPUT_FILENAME, fourcc, fps, (width, height))
        for f in buffer:
            out.write(f)
        out.release()
        print(f"Saved last {BUFFER_SECONDS} seconds to {OUTPUT_FILENAME}")

    elif key == ord('q'):
        break

# === Cleanup ===
cap.release()
cv2.destroyAllWindows()

# class VideoReplaySystem:
