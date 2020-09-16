import cv2
import time
import datetime
from collections import deque
from twilio.rest import Client


def is_person_present(frame, thresh=1100):
    global bg_subtractor

    # Applying background subtraction
    fg_mask = bg_subtractor.apply(frame)

    # Getting rid of the shadows
    ret, fg_mask = cv2.threshold(fg_mask, 250, 255, cv2.THRESH_BINARY)

    # Applying some morphological operations to make the mask better
    fg_mask = cv2.dilate(fg_mask, kernel, iterations=4)

    # Detecting contours in the frame
    contours, hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Check if there was a contour and the area is somewhat higher than the threshold
    # so we know its a person and not noise
    if contours and cv2.contourArea(max(contours, key=cv2.contourArea)) > thresh:

        # Get the max contour
        max_contour = max(contours, key=cv2.contourArea)

        # Draw a bounding box around movement and labelling it
        x, y, w, h = cv2.boundingRect(max_contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, 'Movement', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1, cv2.LINE_AA)
        return True, frame

    # Otherwise report there was no one present
    else:
        return False, frame


def send_message(body, info_dict):
    # Your Account SID from twilio.com/console
    account_sid = info_dict['ACCOUNT_SID']
    # Your Auth Token from twilio.com/console
    auth_token = info_dict['AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    client.messages.create(to=info_dict['ALERT_NUM'], from_=info_dict['TRIAL_NUM'], body=body)


# Setting Window normal so we can resize it
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)

# This is just a recorded video, change it to 0 for webcam
cap = cv2.VideoCapture('sample_video(1).mp4')

# Video stream from IP webcam android app
# cap = cv2.VideoCapture('http://192.168.18.4:8080/video')

# Get width and height of the frame
width = int(cap.get(3))
height = int(cap.get(4))

# Read and store the credentials information in a dict
with open('credentials.txt', 'r') as fileopened:
    data = fileopened.read()

info_dict = eval(data)

# Initialize the background Subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True, varThreshold=50, history=2800)

# Status is True when person is present and False when the person is not present
status = False

# After the person disappears from view, wait atleast 2 seconds before making the status False
patience = 2

# We don't consider an initial detection unless its detected atleast 7 times, this gets rid of false positives
detection_thresh = 7

# Initial time for calculating if patience time is up
initial_time = None

# We are creating a deque object of length detection_thresh and will store individual detection statuses here
de = deque([False] * detection_thresh, maxlen=detection_thresh)

# Initialise these variables for calculating FPS and note the starting time
fps = 0
frame_counter = 0
start_time = time.time()

# setting custom kernel
kernel = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # This function will return a boolean variable telling if someone was present or not,
    # it will also draw boxes if it finds movement
    detected, annotated_image = is_person_present(frame)

    # Register the current detection status on our deque object
    de.appendleft(detected)

    # If we have consecutively detected a person 10 times then we are sure that someone is present
    # We also make this is the first time that this person has been detected so we only initialize the VideoWriter once
    if sum(de) == detection_thresh and not status:
        status = True
        entry_time = datetime.datetime.now().strftime("%A, %I-%M-%S %p %d %B %Y")
        output_video = cv2.VideoWriter('outputs/{}.avi'.format(entry_time), cv2.VideoWriter_fourcc(*'MJPG'), 10,
                                       (width, height))

    # If status is True but the person is not in the current frame
    if status and not detected:
        # Restart the patience timer only if the person has not been detected for a few frames
        # so we are sure it wasn't a False positive
        if sum(de) > (detection_thresh / 2):
            if initial_time is None:
                initial_time = time.time()

        elif initial_time is not None:
            # If the patience has run out and the person is still not detected then set the status to False
            # Also save the video by releasing the video writer and send a text message to the owner.
            if time.time() - initial_time >= patience:
                status = False
                exit_time = datetime.datetime.now().strftime("%A, %I:%M:%S %p %d %B %Y")
                output_video.release()
                initial_time = None

                body = "Alert: \n A Person Entered the Room at {} \n Left the room at {}".format(entry_time, exit_time)
                send_message(body, info_dict)

    # If significant amount of detections i.e., more than half of detection_thresh has occured
    # then we reset the Initial Time.
    elif status and sum(de) > (detection_thresh / 2):
        initial_time = None

    # Getting the current time in the required format
    current_time = datetime.datetime.now().strftime("%A, %I:%M:%S %p %d %B %Y")

    # Displaying the FPS
    cv2.putText(annotated_image, 'FPS: {:.2f}'.format(fps), (510, 450), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 40, 155),
                2)

    # Displaying Time
    cv2.putText(annotated_image, current_time, (250, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)

    # Displaying the Room Status
    cv2.putText(annotated_image, 'MOVEMENT: {}'.format(str(status)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (200, 10, 150), 2)

    # Show the patience Value
    if initial_time is None:
        text = 'Patience: {}'.format(patience)
    else:
        text = 'Patience: {:.2f}'.format(max(0, patience - (time.time() - initial_time)))

    cv2.putText(annotated_image, text, (10, 450), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 40, 155), 2)

    # If status is true save the frame
    if status:
        output_video.write(annotated_image)

    # Show the Frame
    cv2.imshow('frame', frame)

    # Calculating the Average FPS
    frame_counter += 1
    fps = (frame_counter / (time.time() - start_time))

    # Press 'q' to exit
    if cv2.waitKey(30) == ord('q'):
        break

# Release Capture and destroy windows
cap.release()
cv2.destroyAllWindows()
output_video.release()