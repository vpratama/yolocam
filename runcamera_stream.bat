@echo on

:: Activate the Python virtual environment
call yolocamrmq/Scripts/activate

:: Start the Python scripts in new command prompt windows
start cmd /k python streamcam.py 0 rtmp://localhost:1935/live/camera-front
start cmd /k python streamcam.py 1 rtmp://localhost:1935/live/camera-side-1
start cmd /k python streamcam.py 2 rtmp://localhost:1935/live/camera-side-2
start cmd /k python streamcam.py 3 rtmp://localhost:1935/live/camera-back
