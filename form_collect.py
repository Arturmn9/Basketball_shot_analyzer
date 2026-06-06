import cv2
import mediapipe as mp
import csv
import math
import collections

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)

reference_file = input("Reference CSV file (pro shooter): ")
pro_trajectory = []
with open(reference_file, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pro_trajectory.append({
            "elbow_x": float(row["elbow_x"]),
            "elbow_y": float(row["elbow_y"]),
            "wrist_x": float(row["wrist_x"]),
            "wrist_y": float(row["wrist_y"])
        })

ref_first_frame = pro_trajectory[0]
ref_elbow = (ref_first_frame["elbow_x"], ref_first_frame["elbow_y"])
ref_wrist = (ref_first_frame["wrist_x"], ref_first_frame["wrist_y"])

def distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

state = "CALIBRATING" 
stable_frames = 0
user_trajectory = []

# Create a rolling buffer that holds the last 15 frames (roughly 0.5 seconds)
# When it hits 15, appending a new frame automatically drops the oldest one
frame_buffer = collections.deque(maxlen=15) 

while True:
    success, frame = cap.read()
    if not success:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        h, w, _ = frame.shape
        landmarks = results.pose_landmarks.landmark

        shoulder = landmarks[12]
        elbow = landmarks[14]
        wrist = landmarks[16]
        hip = landmarks[24] 

        # -----------------------------
        # 2. SCALE & NORMALIZE LIVE DATA
        # -----------------------------
        scale = math.sqrt((shoulder.x - hip.x)**2 + (shoulder.y - hip.y)**2)
        
        if scale == 0:
            continue

        sx, sy = shoulder.x, shoulder.y

        user_elbow = ((elbow.x - sx) / scale, (elbow.y - sy) / scale)
        user_wrist = ((wrist.x - sx) / scale, (wrist.y - sy) / scale)

        # -----------------------------
        # 3. VISUALIZATION
        # -----------------------------
        sx_px, sy_px = int(shoulder.x * w), int(shoulder.y * h)
        ex_px, ey_px = int(elbow.x * w), int(elbow.y * h)
        wx_px, wy_px = int(wrist.x * w), int(wrist.y * h)

        cv2.circle(frame, (sx_px, sy_px), 10, (0,255,0), -1)
        cv2.circle(frame, (ex_px, ey_px), 10, (0,255,0), -1)
        cv2.circle(frame, (wx_px, wy_px), 10, (0,255,0), -1)

        cv2.line(frame, (sx_px, sy_px), (ex_px, ey_px), (255,0,0), 3)
        cv2.line(frame, (ex_px, ey_px), (wx_px, wy_px), (255,0,0), 3)

        # -----------------------------
        # 4. STATE MACHINE LOGIC
        # -----------------------------
        if state == "CALIBRATING":
            elbow_diff = distance(user_elbow, ref_elbow)
            wrist_diff = distance(user_wrist, ref_wrist)
            total_diff = elbow_diff + wrist_diff

            aligned = total_diff < 0.45 

            if aligned:
                stable_frames += 1
                color = (0, 255, 0)
                cv2.putText(frame, "PERFECT! HOLD STILL", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
            else:
                stable_frames = 0
                color = (0, 0, 255)

            cv2.putText(frame, f"Alignment Score: {round(total_diff, 3)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"Stable Frames: {stable_frames}/30", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            # Trigger READY phase when held
            if stable_frames > 30:
                state = "READY"
                print("Calibration locked! Ready for you to shoot.")

        elif state == "READY":
            cv2.putText(frame, "READY! SHOOT WHEN READY.", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
            
            # Continuously push current position into the rolling memory
            frame_buffer.append({
                "user_elbow_x": user_elbow[0], "user_elbow_y": user_elbow[1],
                "user_wrist_x": user_wrist[0], "user_wrist_y": user_wrist[1]
            })

            # THE TRIGGER: If your wrist moves significantly UP (lower Y value) from the calibration point
            if user_wrist[1] < ref_wrist[1] - 0.15:
                state = "RECORDING"
                print("Shot motion detected! Recording...")
                
                # Flush the memory buffer into the main trajectory to catch the wind-up!
                for buffered_frame in frame_buffer:
                    user_trajectory.append(buffered_frame)

        elif state == "RECORDING":
            cv2.putText(frame, f"RECORDING... {len(user_trajectory)}/{len(pro_trajectory)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            # Save live frame data
            user_trajectory.append({
                "user_elbow_x": user_elbow[0], "user_elbow_y": user_elbow[1],
                "user_wrist_x": user_wrist[0], "user_wrist_y": user_wrist[1]
            })

            # Stop recording once we match the length of the pro video
            if len(user_trajectory) >= len(pro_trajectory):
                state = "DONE"
                print("Recording Complete!")

        elif state == "DONE":
            cv2.putText(frame, "DONE! Press 'q' to save & exit.", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow("Basketball Calibration System", frame)

    key = cv2.waitKey(20) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s') and state in ["CALIBRATING", "READY"]:
        state = "RECORDING"
        print("Manual Override: Recording Started!")

cap.release()
cv2.destroyAllWindows()

# -----------------------------
# 5. SAVE TRAJECTORY COMPARISON
# -----------------------------
if user_trajectory:
    out_file = "trajectory_comparison.csv"
    with open(out_file, "w", newline='') as f:
        fieldnames = [
            "frame", "user_elbow_x", "user_elbow_y", "user_wrist_x", "user_wrist_y",
            "pro_elbow_x", "pro_elbow_y", "pro_wrist_x", "pro_wrist_y"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Stitch your recorded data together with the pro's data frame-by-frame
        for i in range(len(pro_trajectory)):
            # Safety check just in case arrays are slightly mismatched
            if i >= len(user_trajectory):
                break 
                
            row = {
                "frame": i,
                "user_elbow_x": user_trajectory[i]["user_elbow_x"],
                "user_elbow_y": user_trajectory[i]["user_elbow_y"],
                "user_wrist_x": user_trajectory[i]["user_wrist_x"],
                "user_wrist_y": user_trajectory[i]["user_wrist_y"],
                "pro_elbow_x": pro_trajectory[i]["elbow_x"],
                "pro_elbow_y": pro_trajectory[i]["elbow_y"],
                "pro_wrist_x": pro_trajectory[i]["wrist_x"],
                "pro_wrist_y": pro_trajectory[i]["wrist_y"]
            }
            writer.writerow(row)
            
    print(f"Saved trajectory comparison to {out_file}")
    decision = input("Run the animation, if not type 'n': ")
    if decision != 'n':
        with open("animator.py", "r") as fp:
            exec(fp.read())
