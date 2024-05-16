import cv2
from ffmpeg import input, output, run_async

rtmp_server_url = "rtmp://192.168.150.90:1935"  # Use rtmp protocol instead of http

# Set camera settings
camera_width = 1280
camera_height = 720

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

# Set camera properties to improve quality
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus
cap.set(cv2.CAP_PROP_FOCUS, 0)  # Set focus to 0 (manual focus)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)  # Adjust brightness
cap.set(cv2.CAP_PROP_CONTRAST, 50)  # Adjust contrast

process = (
    input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{camera_width}x{camera_height}')
    .output(rtmp_server_url, format='flv', vcodec='libx264', crf=18)  # Use H.264 encoding and adjust quality
    .run_async(pipe_stdin=True)
)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    process.stdin.write(frame.tobytes())

cap.release()
cv2.destroyAllWindows()
process.stdin.close()
process.wait()