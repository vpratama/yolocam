import cv2
import ffmpeg
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description='Streaming Camera with RTMP')
parser.add_argument('video_source', type=int, help='Camera index (e.g., 0 for the first camera)')
parser.add_argument('rtmp_stream_url', type=str, help='RTMP Server URL (e.g., rtmp://localhost:1935/live/camera-front)')

args = parser.parse_args()
rtmp_server_url = args.rtmp_stream_url

# Set camera settings
camera_width = 1280
camera_height = 720
frame_rate = 25  # Set frame rate to match the RTMP server settings

# Initialize camera
cap = cv2.VideoCapture(args.video_source)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

# Set up FFMPEG process for streaming to RTMP
process = (
    ffmpeg
    .input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{camera_width}x{camera_height}', framerate=frame_rate)
    .output(rtmp_server_url, format='flv', vcodec='libx264', pix_fmt='yuv420p', r=frame_rate)
    .run_async(pipe_stdin=True)
)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Write frame to FFMPEG process
        process.stdin.write(frame.tobytes())

except BrokenPipeError:
    print("Stream connection was broken.")

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    process.stdin.close()
    process.wait()
