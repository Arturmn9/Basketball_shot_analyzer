import cv2
import mediapipe as mp
import math

print()

video_name = input("Name of the mp4 file to use: ")
file_name = input("Name of the csv file to save the positions in (format - ____): ")

pose = mp.solutions.pose.Pose()

cap = cv2.VideoCapture(video_name)

fps = cap.get(cv2.CAP_PROP_FPS)

seh_location_arr = []  # shoulder, elbow and hand location array
frame_num = 0

def angle_calc(ax, ay, bx, by, cx, cy):
    '''
    Purpose: Calculate the angle which is made by 3 points, shoulder, elbow and wrist.
    Parameters:
        ax, ay - the x and y coordinates of the shoulder (int/float)
        bx, by - the x and y coordinates of the elbow (int/float)
        cx, cy - the x and y coordinates of the wrist (int/float)
    Return value: The degree value of the angle 
    '''

    # Creates 2 vectors with the coordinateds given (abx, aby, cbx and cby)
    abx = ax - bx
    aby = ay - by
    cbx = cx - bx
    cby = cy - by

    dot_product = abx * cbx + aby * cby

    # Calculates the magnitudes (length) of the 2 vectors 
    mag_ab = math.sqrt(abx ** 2 + aby ** 2)
    mag_cb = math.sqrt(cbx ** 2 + cby ** 2)

   
    # If any of the vectors does not have a length no angle is possible
    if mag_ab == 0 or mag_cb == 0:
        return 0
    
    # Calculate the cosine of the angle
    cos_theta = dot_product / (mag_ab * mag_cb)

    # make sure the value is not higher than 1, because of the issue with 
    # the python float values
    cos_theta = max(-1.0, min(1.0, cos_theta))

    return math.degrees(math.acos(cos_theta))

while True:

    success, frame = cap.read()

    if not success:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb)

    if not results.pose_landmarks:
        print(f"The landmarks were not found for frame {frame_num}")

    else:

        landmarks = results.pose_landmarks.landmark

        shoulder = landmarks[12]  # right shoulder
        elbow = landmarks[14]     # right elbow
        wrist = landmarks[16]     # right wrist
        hip = landmarks[24]       # right hip

        # skip unreliable detections
        if (
            shoulder.visibility < 0.5
            or elbow.visibility < 0.5
            or wrist.visibility < 0.5
            or hip.visibility < 0.5
        ):
            frame_num += 1
            continue
        
        # scale based on body size
        scale = math.sqrt(
            (shoulder.x - hip.x) ** 2 +
            (shoulder.y - hip.y) ** 2
        )

        if scale == 0:
            frame_num += 1
            continue
    
        # coordinates relative to shoulder
        ex = (elbow.x - shoulder.x) / scale
        ey = (elbow.y - shoulder.y) / scale

        wx = (wrist.x - shoulder.x) / scale
        wy = (wrist.y - shoulder.y) / scale

        elbow_angle = angle_calc(
            shoulder.x,
            shoulder.y,
            elbow.x,
            elbow.y,
            wrist.x,
            wrist.y
        )

        seh_location_arr.append({
            "frame": frame_num,
            "time": frame_num / fps,
            "elbow_x": ex,
            "elbow_y": ey,
            "wrist_x": wx,
            "wrist_y": wy,
            "elbow_angle": elbow_angle
        })

    frame_num += 1

cap.release()

if seh_location_arr:

    with open(file_name + ".csv", "w") as fp:

        fp.write(
            "frame,time,elbow_x,elbow_y,"
            "wrist_x,wrist_y,elbow_angle\n"
        )

        for member in seh_location_arr:

            fp.write(
                f"{member['frame']},"
                f"{member['time']},"
                f"{member['elbow_x']},"
                f"{member['elbow_y']},"
                f"{member['wrist_x']},"
                f"{member['wrist_y']},"
                f"{member['elbow_angle']}\n"
            )

print(f"Saved {len(seh_location_arr)} frames to {file_name}.csv")