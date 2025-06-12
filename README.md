# Video Replay System

A simple video replay system that continuously records from a camera and allows you to save the last few seconds of footage on demand.

## Features

- Continuously captures video from a webcam or USB camera
- Maintains a buffer of the most recent frames (configurable duration)
- Save replays with a single keystroke
- Automatically generates timestamped filenames
- Object-oriented design for easy customization

## Requirements

- Python 3.6+
- OpenCV (`opencv-python`)
- NumPy

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install opencv-python numpy
```

## Usage

Run the program:

```bash
python VideoReplaySystem.py
```

### Default Controls

- Press `s` to save the replay (last 5 seconds of footage)
- Press `q` to quit the application

### Customization

You can customize the replay system by modifying the parameters when creating the `VideoReplaySystem` object:

```python
# Example with custom settings
replay_system = VideoReplaySystem(
    camera_index=0,           # Camera device index (0 = first camera)
    buffer_seconds=10,        # Keep 10 seconds of video instead of the default 5
    output_filename=None,     # Auto-generate filename with timestamp
    trigger_key=ord('r'),     # Press 'r' to save replay instead of 's'
    quit_key=ord('x')         # Press 'x' to quit instead of 'q'
)
```

### USB Camera Support

The system automatically works with USB cameras. If you have multiple cameras connected, you can select a specific camera by changing the `camera_index` parameter (0, 1, 2, etc.).

## How It Works

1. The system continuously captures frames from the camera
2. Frames are stored in a circular buffer (deque) with a maximum length
3. When the trigger key is pressed, all frames in the buffer are saved to a video file
4. The buffer continues to update, allowing for multiple replays to be saved

## License

MIT License
