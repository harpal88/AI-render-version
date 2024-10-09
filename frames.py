import cv2
import os
import time

def extract_frames(video_path, output_folder, interval):
    # Added delay to ensure the file is fully available
    time.sleep(2)  # Optional: wait before retrying

    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print(f"Error: Could not open video file {video_path}.")
        return
    
    fps = video.get(cv2.CAP_PROP_FPS)
    
    if fps == 0:
        print("Error: Could not retrieve FPS from the video.")
        return

    frame_interval = int(fps * interval)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    count = 0
    frame_number = 0
    success, frame = video.read()

    while success:
        if frame_number % frame_interval == 0:
            frame_file = os.path.join(output_folder, f"frame_{count:04d}.jpg")
            cv2.imwrite(frame_file, frame)
            print(f"Saved frame: {frame_file}")
            count += 1
        
        success, frame = video.read()
        frame_number += 1

    video.release()

# Example usage with some delay before processing
extract_frames('results/v.mp4', 'output_frames', interval=0.65)
