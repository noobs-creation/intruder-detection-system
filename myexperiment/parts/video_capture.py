import cv2
import time

# Set Window to normal so that it is resizeable
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)

# Note start time and Initialize variables for calculating FPS
start_time = time.time()
fps = 0
fps_counter = 0

# Video stream from the web-cam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Calculating the Average FPS
    fps_counter += 1
    fps = (fps_counter / (time.time() - start_time))

    # Displaying the FPS
    cv2.putText(frame, 'FPS: {:.1f}'.format(fps), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # Show the frames in a window
    cv2.imshow('frame', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) == ord('q'):
        break

# Release and destroy windows
cap.release()
cv2.destroyAllWindows()