### INTRUDER DETECTOR SYSTEM

A very simple system to detect any kind of movement or motion in a given area. Though here we are using sample recorded video. You guys can change the code for using webcam or
get the link from IP WebCam android app, though both PC and mobile phone must be connected to the same network.
You can go through 'parts' folder and there I worked on each working part separately.


#### Requirements 

```
pip install opencv-python
pip install twilio
```

#### Twilio API

goto Twilio website, and create a free account, you will be provided
free TRIAL_NUM and ACCOUNT_SID and AUTH_TOKEN, you need to enter manually you phone number in credentials.txt - ALERT_NUM, similarly replace others too.

#### Running 

```bash
python intruder_detection_system.py
```


