# Basketball Shot Analyzer

A computer vision tool that compares your basketball shooting form to a professional's. It tracks your shoulder, elbow, and wrist with MediaPipe, normalizes the data so body size does not matter, and lets you replay both shots on top of each other.

Built with Python, OpenCV, MediaPipe, and NumPy.

## How it works

1. **Extract a reference form.** `form_extract.py` reads a video of a shooter, finds the right shoulder, elbow, and wrist in each frame, and saves the positions and elbow angle to a CSV. Positions are measured relative to the shoulder and divided by the shoulder-to-hip distance, so the data does not depend on how big the person is or how far they stand from the camera. Elbow angle comes from the dot product of the upper-arm and forearm vectors.
2. **Record your own shot.** `form_collect.py` opens your webcam and shows a live alignment score against the reference. When you are lined up and hold still, it locks in. A rolling 15-frame buffer watches your wrist, and when it sees the upward shooting motion it starts recording automatically, keeping the frames from just before the motion.
3. **Compare.** `animator.py` plays both motions in an OpenCV window with a timeline slider and frame-by-frame stepping (`A` / `D`).

## Setup

Requires Python 3.8+ and a working webcam.

```
pip install -r requirements.txt
```

## Usage

1. Get an `.mp4` of a shooter, filmed from the shooter's right side.
2. Run `python form_extract.py`. Enter the video file name (for example `shot.mp4`), then a name for the output file. Do not add `.csv`; it is added for you.
3. Run `python form_collect.py`. Enter the CSV file name **with** `.csv`.
4. Stand in a similar position to the video. Recording becomes available when the alignment score is 0.45 or lower.
5. Shoot with your whole arm in view.
6. When asked, press Enter to run the animation, or type `n` to skip it. You can also run `python animator.py` any time.

Press `Q` to quit. Press `S` during calibration to start recording manually.

## Files

| File | Purpose |
| --- | --- |
| `form_extract.py` | Extracts normalized joint data from a video |
| `form_collect.py` | Live calibration and recording from the webcam |
| `animator.py` | Overlay playback with timeline slider |
| `currysform.csv` | Example reference form |
| `trajectory_comparison.csv` | Example output of a comparison |

## Limitations

- Tracks the right arm only, so shoot right-handed and film from the right side.
- Works best with one person in frame and a clear view of the whole arm.
