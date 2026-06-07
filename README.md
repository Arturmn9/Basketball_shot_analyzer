# Basketball_shot_analyzer
Project that analyzes basketball shooting form, using Python, OpenCV, MediaPipe and NumPy. It normalizes human pose data so it is possible to compare to real-time shooting trajectory against other or professional players.

## Features
* **Biomaechanical Data Extraction:** Parses a reference video and maps the joint angles using linear algebra principles and scaling normalization in order to make the data for different sized objects, then saves the information as a CSV file.
* **Real Time Calibaration:** Interactive UI guids the user into a correct position.
* **Automated Motion Trigger:** Uses a rolling memory buffer to detect the upward wrist velocity and trigger the recording without manual recording.
* **Interactive Playback** Custom timeline to watch the 2 shot forms overlaid.

 ## Prerequisites
 Before you begin, ensure that you have the following things installed:

* Python 3.8 or higher
* Webcam (that works)

