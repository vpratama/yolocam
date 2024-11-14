@echo off

:: Activate the Python virtual environment
call yolocamrmq/Scripts/activate

:: Start the Python scripts in new command prompt windows
start cmd /k python yolocamrmq.py 0 camera-front
start cmd /k python yolocamrmq.py 1 camera-side-1
start cmd /k python yolocamrmq.py 2 camera-side-2
start cmd /k python yolocamrmq.py 3 camera-back

:: Run cartesian program
