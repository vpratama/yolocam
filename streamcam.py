import cv2
from ffmpeg import input, output, run_async

rtmp_server_url = "rtmp://localhost:1935"

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

process = (
    input('pipe:', format='rawvideo', pix_fmt='bgr24', s='640x480')
    .output(rtmp_server_url, format='flv')
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