# Raspberry Pi Streaming code
Import required Packages
```python
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import socket
import struct
import pickle
```

initialize the camera and grab a reference to the raw camera capture
```python
clientsocket = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
clientsocket.connect(('2620:cc:8000:1c83:c50e:9548:f2fc:d239',8000,0,0)) #2620:cc:8000:1c83:852e:3cb3:b8c9:ff54
camera = PiCamera()
camera.resolution = (1920,480)
camera.framerate = 2
rawCapture = PiRGBArray(camera, size=(1920,480))
 ```
Allow the camera to warmup

```python
time.sleep(0.1)
```

capture frames from the camera and sends it to the connected socket server
```python
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    data = pickle.dumps(image)
    clientsocket.sendall(struct.pack("<L", len(data))+data)
    # show the frame
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
 
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
 
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
'''
