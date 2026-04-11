# Video Replay System
# Libraries used: pip3.13 opencv-python numpy
import os
import numpy as np
import cv2
import collections
import time
import threading
from datetime import datetime
from pathlib import Path

'''
TODO: Implament a checker for the OS running the code to use the best available hardware encoding
        Platform 	    Hardware Encoder Framework	        Hardware Requirements
        Mac/Apple	        VideoToolbox	                    Apple Silicon (M1/M2/M3) or Intel Macs
        Windows	            NVENC	                            NVIDIA Graphics Cards
        Windows	            QuickSync (QSV)	                    Intel CPUs with Integrated Graphics
        Windows	            VCE / AMF	                        AMD CPUs with Graphics Cards

        
'''


"""sumary_line

Keyword arguments:
argument -- description
Return: return_description
"""
class VideoReplaySystem:
    def __init__(self, camera_index=0, buffer_seconds=5, output_filename=None, 
                 trigger_key=ord('s'), quit_key=ord('q'), codec='mp4v', 
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
        self.trigger_delay = 1
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
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) #or 30  # fallback to 30 if undetectable
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Measure actual FPS if the reported FPS is 0 or unrealistic
        if self.fps <= 0 or self.fps > 1000:
            try:
                self.fps = int(self.measure_fps())
                print(f"Corrected FPS: {self.fps}, after measuring")

                if self.fps <= 0:
                    print("Measured FPS is still invalid. Defaulting to 30 FPS.")
                    self.fps = 30                
            except Exception as e:
                print(f"Error measuring FPS: {e}")
                self.fps = 30  # fallback to 30 if measurement fails
        
        # Initialize buffer
        buffer_size = self.fps * (self.buffer_seconds + self.trigger_delay)
        self.buffer = collections.deque(maxlen=buffer_size)
        
        print(f"Capture started: {self.width}x{self.height} at {self.fps} FPS")
        print(f"Buffer size: {buffer_size} frames ({self.buffer_seconds} seconds)")
        print(f"Press '{chr(self.trigger_key)}' to save replay, '{chr(self.quit_key)}' to quit")
    
    """Check the true FPS from Camera if it returns a silly number with cv2.CAP_PROP_FPS
    
    Keyword arguments:
    num_frames -- number of frames to capture for measurement (default: 120)
    Return: measured_fps -- the calculated fps based on time taken to capture
    """
    def measure_fps(self, num_frames=120):
        """
        Measure the actual FPS 
        count 120 frames
        measure time it takes to recieve all frames
        """
        def frame_gen():
            """Generator to yield frames from the camera."""
            if self.cap is not None:
                for i in range(num_frames):
                    ret, frame = self.cap.read()
                    if not ret:
                        print("Frame capture failed during FPS measurement.")
                        break
                    yield frame
            else:
                print("Camera is not initialized so cannot measure FPS.")

        warmup_frames = 10 # Number of initial frames to skip for warm-up

        camera = self.cap
        if camera is None or not camera.isOpened():
            print("Camera is not initialized for FPS measurement.")
            return 0
        else: 
            print(f"Starting Fps measurement with: {num_frames} frames ")
            # start = time.time() # Start time at frame 0
            start = int(0) # declare start variabele
            
            for frame_number, frame in enumerate(frame_gen(), start=0):
                # ret, frame = camera.read() # Read a frame from the camera, then start the timer
                if frame_number == warmup_frames:
                    start = time.time() # Start time after 10 frames for more accurate measurement (skip initial frames which may be slower)

            
            end = time.time()
            # Calculate seconds elapsed and actual FPS
            seconds = end - start

            if seconds > 0:
                measured_fps = (num_frames - warmup_frames) / seconds 
                print(f"Measured FPS: {measured_fps:.2f}")
                return measured_fps
            else:
                print("Time measurement error during FPS calculation. seconds not > 0")
                return 0
        



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
                    start_time = time.time()
                    # Continue recording for 1 more second
                    while time.time() - start_time < 1.0:
                        ret, frame = self.cap.read()
                        if not ret:
                            break
                        self.buffer.append(frame)
                        # if self.display_preview:
                        #     cv2.imshow('Live Feed', frame)
                        # cv2.waitKey(1)
                    # when the trigger fires snapshot the current buffer and save it in a separate thread:
                    if self.buffer is not None:
                        frames = list(self.buffer)  # Snapshot of current buffer
                        threading.Thread(target=self.save_replay, args=(frames,)).start()   

                elif key == self.quit_key:
                    break
                    
        finally:
            self.cleanup()
    
    # Save frames as a parameter instead of reading self.buffer directly
    def save_replay(self, frames):
        """Save the current buffer to a video file."""
        if not frames:
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
        for frame in frames:
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