# Video Replay System
# Libraries used: pip3.13 opencv-python numpy
import os
import numpy as np
import cv2
import collections
from datetime import datetime
from pathlib import Path


class VideoReplaySystem:
    def __init__(self, camera_index=0, buffer_seconds=5, output_filename=None, 
                 trigger_key=ord('s'), quit_key=ord('q'), codec='XVID', 
                 resolution=None, display_preview=True, save_dir="SavedReplays"):
        """
        Initialize the video replay system.
        
        Args:
            camera_index: Camera device index (0 is usually the first webcam/USB camera)
            buffer_seconds: Number of seconds to keep in the buffer
            output_filename: Filename for saved videos (if None, uses timestamp)
            trigger_key: Key to press to save the replay
            quit_key: Key to press to quit the application
            codec: FourCC codec for the output video
            resolution: Optional tuple (width, height) to set camera resolution
            display_preview: Whether to show a preview window
            save_dir: Directory to save replay files (default: "SavedReplays")
        """
        self.camera_index = camera_index
        self.buffer_seconds = buffer_seconds
        self.output_filename = output_filename
        self.trigger_key = trigger_key
        self.quit_key = quit_key
        self.codec = codec
        self.resolution = resolution
        self.display_preview = display_preview
        self.save_dir = save_dir
        
        # Create save directory if it doesn't exist
        save_path = Path(self.save_dir)
        save_path.mkdir(exist_ok=True, parents=True)
        
        # Initialize capture
        self.cap = None
        self.buffer = None
        self.fps = 0
        self.width = 0
        self.height = 0
        self.fourcc = cv2.VideoWriter_fourcc(*self.codec)
        
    def start_capture(self):
        """Initialize and start the video capture."""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at index {self.camera_index}")
        
        # Set resolution if provided
        if self.resolution:
            width, height = self.resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
        # Get video properties
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 30  # fallback to 30 if undetectable
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Initialize buffer
        buffer_size = self.fps * self.buffer_seconds
        self.buffer = collections.deque(maxlen=buffer_size)
        
        print(f"Capture started: {self.width}x{self.height} at {self.fps} FPS")
        print(f"Buffer size: {buffer_size} frames ({self.buffer_seconds} seconds)")
        print(f"Press '{chr(self.trigger_key)}' to save replay, '{chr(self.quit_key)}' to quit")
        
    def run(self):
        """Run the main capture and processing loop."""
        if self.cap is None or not self.cap.isOpened():
            self.start_capture()
            
        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    print("Frame capture failed. Exiting.")
                    break

                self.buffer.append(frame)

                # Display preview if enabled
                if self.display_preview:
                    cv2.imshow('Live Feed', frame)

                key = cv2.waitKey(1) & 0xFF

                if key == self.trigger_key:
                    self.save_replay()
                elif key == self.quit_key:
                    break
                    
        finally:
            self.cleanup()
    
    def save_replay(self):
        """Save the current buffer to a video file."""
        if not self.buffer:
            print("Buffer is empty. Nothing to save.")
            return
            
        # Generate filename with timestamp if not provided
        if self.output_filename:
            filename = self.output_filename
            # If just a filename without path, add save_dir
            if not os.path.dirname(filename):
                filename = os.path.join(self.save_dir, filename)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.save_dir, f"replay_{timestamp}.mp4")
            
        print(f"Saving replay to {filename}...")
        
        out = cv2.VideoWriter(filename, self.fourcc, self.fps, (self.width, self.height))
        for frame in self.buffer:
            out.write(frame)
        out.release()
        
        print(f"Saved last {self.buffer_seconds} seconds to {filename}")
    
    def cleanup(self):
        """Release resources."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Cleanup complete")



# Example usage
if __name__ == "__main__":
    # Create and run the video replay system
    replay_system = VideoReplaySystem(
        camera_index=0,           # First camera (usually webcam or USB camera)
        buffer_seconds=5,         # Keep 5 seconds of video
        output_filename=None,     # Use auto-generated filename based on timestamp
        trigger_key=ord('s'),     # Press 's' to save
        quit_key=ord('q'),        # Press 'q' to quit
        save_dir="SavedReplays",  # Directory to save replay files
        resolution=None,          # Use default camera resolution
        display_preview=True      # Show preview window
    )
    replay_system.run()