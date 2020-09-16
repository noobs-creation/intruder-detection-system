import numpy as np
import cv2

'''
# loading a recorded video
cap = cv2.VideoCapture('sample_video.mp4')

# Creating the background subtractor object
bg_Subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True, varThreshold=50, history=2800)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply the background object on each frame
    fg_mask = bg_Subtractor.apply(frame)

    # Getting rid of the shadows
    ret, fg_mask = cv2.threshold(fg_mask, 250, 255, cv2.THRESH_BINARY)

    # Show the background subtraction frame
    cv2.imshow('Background substraction frame', fg_mask)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()'''

# initialise video capture object
cap = cv2.VideoCapture('sample_video(1).mp4')

# you can set custom kernel size if you want
kernel = None

'''
detectShadows: This parameter gives us the option to detect and get rid of shadows for smooth and robust results.
 Though enabling shadow detection slightly decreases speed.

history: This parameter is the number of frames that is used to create the background model.

varThreshold: This parameter helps filtering out noise present in the frame,
 increasing this number helps if there are lots of white spots in the frame.
 Although we will use morphological operations like dilation and erosion to get rid of noise.'''
# Creating the background subtractor object
bg_Subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True, varThreshold=50, history=2800)

# Setting noise filter threshold
thresh = 1100

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply background subtraction
    fg_mask = bg_Subtractor.apply(frame)

    # Get rid of the shadows
    ret, fg_mask = cv2.threshold(fg_mask, 250, 255, cv2.THRESH_BINARY)

    # Applying some morphological operations to make the mask better, you can play around with this
    fg_mask = cv2.erode(fg_mask, kernel, iterations=1)
    fg_mask = cv2.dilate(fg_mask, kernel, iterations=4)

    # Detecting contours in the frame
    contours, hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get the maximum contour
        max_contour = max(contours, key=cv2.contourArea)

        # we need to make sure the contour area is higher than threshold
        # to make sure its a person and not some noise
        if cv2.contourArea(max_contour) > thresh:
            # Drawing a bounding box around the movement area and labelling it
            x, y, w, h = cv2.boundingRect(max_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, 'Movement', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1,
                        cv2.LINE_AA)

    # Displaying background subtractor on the recorded video
    # cv2.imshow('Background substraction frame', fg_mask)

    # Stacking both frames horizontally and displaying it for comparison
    fg_mask_3 = cv2.cvtColor(fg_mask, cv2.COLOR_GRAY2BGR)
    stacked = np.hstack((fg_mask_3, frame))
    cv2.imshow('Combined view', cv2.resize(stacked, None, fx=0.65, fy=0.65))

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
