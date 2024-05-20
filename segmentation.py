import cv2

# open the video file
cap = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Error opening camera")
    exit()

# Set the frame width and height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Define color ranges for street, wall, and sky
lower_street = (0, 0, 100)
upper_street = (100, 50, 255)
lower_wall = (0, 100, 0)
upper_wall = (100, 255, 100)
lower_sky = (100, 100, 100)
upper_sky = (150, 255, 255)

while True:
    # read a frame from the video
    ret, frame = cap.read()

    # check if the frame was successfully read
    if not ret:
        break

    # convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # create masks for street, wall, and sky using color thresholding
    mask_street = cv2.inRange(hsv, lower_street, upper_street)
    mask_wall = cv2.inRange(hsv, lower_wall, upper_wall)
    mask_sky = cv2.inRange(hsv, lower_sky, upper_sky)

    # apply morphological operations to remove noise and fill holes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_street = cv2.morphologyEx(mask_street, cv2.MORPH_CLOSE, kernel)
    mask_wall = cv2.morphologyEx(mask_wall, cv2.MORPH_CLOSE, kernel)
    mask_sky = cv2.morphologyEx(mask_sky, cv2.MORPH_CLOSE, kernel)
    mask_street = cv2.morphologyEx(mask_street, cv2.MORPH_OPEN, kernel)
    mask_wall = cv2.morphologyEx(mask_wall, cv2.MORPH_OPEN, kernel)
    mask_sky = cv2.morphologyEx(mask_sky, cv2.MORPH_OPEN, kernel)

    # apply bitwise operations to combine the masks
    mask = cv2.bitwise_or(mask_street, mask_wall)
    mask = cv2.bitwise_or(mask, mask_sky)

    # apply Canny edge detection to the mask
    edges = cv2.Canny(mask, 50, 150)

    # apply HoughLinesP to detect lines in the image
    lines = cv2.HoughLinesP(edges, 1, 3.1415/180, 50, minLineLength=200, maxLineGap=10)

    # check if lines is not None before iterating over it
    if lines is not None:
        # iterate over the lines and draw them on the frame
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # apply bitwise operations to segment the street, wall, and sky
    street = cv2.bitwise_and(frame, frame, mask=mask_street)
    wall = cv2.bitwise_and(frame, frame, mask=mask_wall)
    sky = cv2.bitwise_and(frame, frame, mask=mask_sky)

    # apply color mapping tothe segmented regions
    street = cv2.cvtColor(street, cv2.COLOR_BGR2GRAY)
    wall = cv2.cvtColor(wall, cv2.COLOR_BGR2HSV)
    wall[..., 0] = 0
    wall[..., 1] = 0
    wall[..., 2] = 255
    sky = cv2.cvtColor(sky, cv2.COLOR_BGR2HSV)
    sky[..., 0] = 120
    sky[..., 1] = 255
    sky[..., 2] = 255

    # display the resulting frames
    cv2.imshow("frame", frame)
    cv2.imshow("street", street)
    cv2.imshow("wall", wall)
    cv2.imshow("sky", sky)

    # exit the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()