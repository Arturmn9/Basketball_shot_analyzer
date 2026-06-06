import cv2
import numpy as np
import csv

filename = "trajectory_comparison.csv"

WIDTH = 800
HEIGHT = 800
SHOULDER_X = 400
SHOULDER_Y = 600 
VISUAL_SCALE = 350 

frames_data = []

try:
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            frames_data.append(row)
except FileNotFoundError:
    print(f"Error: Could not find '{filename}'.")
    exit()

total_frames = len(frames_data)
if total_frames == 0:
    print("Error: No data found in CSV.")
    exit()

def draw_skeleton(frame_index):
    """Draws a specific frame of the trajectory onto the canvas."""
    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    row = frames_data[frame_index]
    
    u_ex, u_ey = float(row["user_elbow_x"]), float(row["user_elbow_y"])
    u_wx, u_wy = float(row["user_wrist_x"]), float(row["user_wrist_y"])
    
    p_ex, p_ey = float(row["pro_elbow_x"]), float(row["pro_elbow_y"])
    p_wx, p_wy = float(row["pro_wrist_x"]), float(row["pro_wrist_y"])

    user_elbow_px = (int(SHOULDER_X + u_ex * VISUAL_SCALE), int(SHOULDER_Y + u_ey * VISUAL_SCALE))
    user_wrist_px = (int(SHOULDER_X + u_wx * VISUAL_SCALE), int(SHOULDER_Y + u_wy * VISUAL_SCALE))
    
    pro_elbow_px = (int(SHOULDER_X + p_ex * VISUAL_SCALE), int(SHOULDER_Y + p_ey * VISUAL_SCALE))
    pro_wrist_px = (int(SHOULDER_X + p_wx * VISUAL_SCALE), int(SHOULDER_Y + p_wy * VISUAL_SCALE))

    shoulder_px = (SHOULDER_X, SHOULDER_Y)

    cv2.line(canvas, shoulder_px, pro_elbow_px, (255, 150, 0), 4) 
    cv2.line(canvas, pro_elbow_px, pro_wrist_px, (255, 150, 0), 4) 
    cv2.circle(canvas, pro_elbow_px, 8, (255, 0, 0), -1) 
    cv2.circle(canvas, pro_wrist_px, 8, (255, 0, 0), -1) 

    cv2.line(canvas, shoulder_px, user_elbow_px, (0, 0, 255), 6) 
    cv2.line(canvas, user_elbow_px, user_wrist_px, (0, 0, 255), 6)
    cv2.circle(canvas, user_elbow_px, 10, (0, 255, 255), -1) 
    cv2.circle(canvas, user_wrist_px, 10, (0, 255, 255), -1) 
    
    cv2.circle(canvas, shoulder_px, 12, (255, 255, 255), -1)

    cv2.putText(canvas, "Pro Shooter (Blue)", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 150, 0), 2)
    cv2.putText(canvas, "You (Red)", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    cv2.putText(canvas, "CONTROLS:", (WIDTH - 300, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(canvas, "'A' - Previous Frame", (WIDTH - 300, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(canvas, "'D' - Next Frame", (WIDTH - 300, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(canvas, "Drag Slider to Scrub", (WIDTH - 300, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(canvas, "'Q' - Quit", (WIDTH - 300, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    cv2.putText(canvas, f"Frame: {frame_index}/{total_frames-1}", (20, HEIGHT - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return canvas

cv2.namedWindow("Skeleton Replay")

cv2.createTrackbar("Timeline", "Skeleton Replay", 0, total_frames - 1, lambda x: None)

print("Playback interface ready.")

current_frame = 0

while True:
    current_frame = cv2.getTrackbarPos("Timeline", "Skeleton Replay")
    
    canvas = draw_skeleton(current_frame)
    cv2.imshow("Skeleton Replay", canvas)

    key = cv2.waitKey(30) & 0xFF

    if key == ord('q'):
        break
    
    elif key == ord('a'):
        new_frame = max(0, current_frame - 1)
        cv2.setTrackbarPos("Timeline", "Skeleton Replay", new_frame)
    
    elif key == ord('d'):
        new_frame = min(total_frames - 1, current_frame + 1)
        cv2.setTrackbarPos("Timeline", "Skeleton Replay", new_frame)

cv2.destroyAllWindows()