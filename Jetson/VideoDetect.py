import io
import os
import socket
import struct
import numpy as np
import cv2
import pickle
import jetson.inference
import jetson.utils
import scipy.misc
import argparse
import json
from PIL import Image
from operator import itemgetter 



# Reads a stored image from file and detects presence of cars
def detectFunc():
	global spot, frameRs, parkingCenters, xlist
	img, width, height = jetson.utils.loadImageRGBA("CarPark.jpeg")
	os.remove("CarPark.jpeg")
	detections = net.Detect(img, width, height)
	for detection in detections:
		if detection.ClassID == 3 and detection.Width < 400 and detection.Height < 400 and detection.Width > 50 and detection.Height > 50:
			frameRs = cv2.rectangle(frameRs,(int(detection.Left), int(detection.Bottom)),(int(detection.Right),int(detection.Top)),(255,0,0),2)
			seen = 0
			for x,y in parkingCenters.items():
				if int(detection.Left)<= y['X'] <= int(detection.Right) and int(detection.Bottom) >= y['Y'] >= int(detection.Top):
					seen = 1
					y['freq'] = y['freq']+1
					print(seen)
					break
			if seen == 0:
				
				point = {
					'X' : int((detection.Left+detection.Right)/2),
					'Y' : int((detection.Top+detection.Bottom)/2),
					'freq' : 1
				}
				xlist.append(point)
				print(xlist)
				print(parkingCenters)		
				parkingCenters["spot"+str(spot)] = point
				spot+=1
			print(detection)
	
	cv2.imshow('Frame',frameRs)


#Reads a video of the parking lot, saves frame as image for detectFunc() to read and calls it, then shows detctions in Cv2 Window
def readFromVideo():
	global frameRs
	cap = cv2.VideoCapture(opt.video)
	if (cap.isOpened()== False): 
		print("Error opening video stream or file")
 
	# Read until video is completed
	while(cap.isOpened()):
  	# Capture frame-by-frame
		ret, frame = cap.read()
		if ret == True:
			frameRs=cv2.resize(frame, (1248,384))
			cv2.imwrite("CarPark.jpeg", frameRs)
	    
			detectFunc()
			# Press Q on keyboard to  exit
			if cv2.waitKey(25) & 0xFF == ord('q'):
				print(parkingCenters) 
				break
		# Break the loop
		else: 
			break

	# When everything done, release the video capture object
	saveToJSON()
	cap.release()

def readFromStream():
	global frameRs
	HOST = ''
	PORT = 8000

	s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	print('Socket created')

	s.bind((HOST, PORT,0,0))
	print('Socket bind complete')
	s.listen(10)
	print('Socket now listening')

	conn, addr = s.accept()

	data = b'' ### CHANGED
	payload_size = struct.calcsize("<L") ### CHANGED
	print(payload_size)
	while True:
	    # Retrieve message size
		try:
			while len(data) < payload_size:
				data += conn.recv(4096)
				print(len(data))

			packed_msg_size = data[:payload_size]
			print(packed_msg_size)
			data = data[payload_size:]
			msg_size = struct.unpack("<L", packed_msg_size)[0] ### CHANGED
			print(msg_size)
		   	# Retrieve all data based on message size
			while len(data) < msg_size:
				data += conn.recv(4096)
    	  
			frame_data = data[:msg_size]
			data = data[msg_size:]
		
		   # Extract frame
			frame = pickle.loads(frame_data)
			frameRs= frame
			cv2.imwrite("CarPark.jpeg", frameRs)
			key = cv2.waitKey(1)
			detectFunc()
			saveToJSON()
		except KeyboardInterrupt:
			cv2.destroyAllWindows()
			break
	    # Display
	
	conn.close()	
	
	    
def saveToJSON():
	# Have to save parkingCenters Object to JSON File to be read by another script to be loaded to a server
	global parkingCenters, xlist
	
	sl = sorted(xlist, key=itemgetter('X'))
	for i in range(len(sl)):
		for X in sl[i]:
			if X == 'Y':
				yY = sl[i][X]
			elif X == 'X':
				xX = sl[i][X]
			else:
				xF = sl[i][X]
		item={
		'Y' : yY,
		'X' : xX,
		'freq' : xF
		}
		if xF >= 1:
			sp[(i+1)] = item
	
	with open(opt.video +'.json', 'w') as fp:
		json.dump(sp, fp)
	#with open('Spots.json', 'w') as fp:
		#json.dump(parkingCenters, fp)

#read any required arguement
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
						   formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-inception-v2", help="pre-trained model to load, see below for options")
parser.add_argument("--threshold", type=float, default=0.1, help="minimum detection threshold to use")
parser.add_argument("--camera", type=str, default="0", help="index of the MIPI CSI camera to use (NULL for CSI camera 0)\nor for VL42 cameras the /dev/video node to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=1280, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")
parser.add_argument("--detectionFrom", type=str, default="video", help="Set value as 'stream' for streaming from raspberry pi")
parser.add_argument("--video", type=str, default="bandiTrain.mp4", help="Set the name the video")
opt, argv = parser.parse_known_args()

# load the object detection network
net = jetson.inference.detectNet(opt.network, argv, opt.threshold)
display = jetson.utils.glDisplay()


# initialize variables
parkingCenters ={}
sp = {}
spot = 1
frameRs = []
xlist =[]


# Check if camera opened successfully
if opt.detectionFrom == 'video' :
	readFromVideo()
else:
	readFromStream()
	


# Closes all the frames
cv2.destroyAllWindows()


