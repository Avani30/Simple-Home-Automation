import RPi.GPIO as GPIO
from multiprocessing import Process
import picamera
import pyrebase
import string
import random
import time
import datetime
import os

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
IR_PIN = 22
LED_PIN = 24
GPIO.setup(IR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)
nextImg = 0
db = None
storage = None

def snapPhoto():
	global nextImg
	global db
	global storage

	with picamera.PiCamera() as camera:
		# Get the camera ready
		rndStr = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(10))
		rndStr += '.jpg'
		time.sleep(1)
		camera.capture(rndStr)
		timeStmp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
		data = {
			'key':rndStr,
			'time': timeStmp,
			'url':rndStr
		}
		db.child('Camera').child('data{0}'.format(nextImg)).set(data)
		nextImg = nextImg + 1
		print("Capturing Picture")
		while (not os.path.exists(rndStr)):
			time.sleep(1)
		print(os.path.exists(rndStr))
		storage.child(rndStr).put(rndStr)
		print("Photo taken")
		return

def runCameraPreview():
	print("Starting process")
	# try image capture in a separate process
	p1 = Process(target=snapPhoto)
	p1.start()
	# Do any processing
	print("Waiting")
	p1.join() # Wait for the process to return
	print('Done!')

if __name__=='__main__':
	
	config = {
		"apiKey": "AIzaSyBrt71aZg5DiyAxyM11no3I-Sh-YcNRarA",
		"authDomain": "homeautomation-23271.firebaseapp.com",
		"databaseURL": "https://homeautomation-23271.firebaseio.com",
		"projectId": "homeautomation-23271",
		"storageBucket": "homeautomation-23271.appspot.com",
		"serviceAccount": "/home/pi/Desktop/homeautomation_key.json",
		"messagingSenderId": "49654542697"
	}

	firebase = pyrebase.initialize_app(config)
	db = firebase.database()
	storage = firebase.storage()

	initData = db.child('Camera').get()
	if (initData.val()):
		nextImg = len(initData.val())+1
	else:
		nextImg = 1
	print(nextImg)
	print('Ready')

	while True:
		current = GPIO.input(IR_PIN)
		if current:
			GPIO.output(LED_PIN, GPIO.HIGH)
			print ('object detected')
			snapPhoto()
			GPIO.output(LED_PIN, GPIO.LOW)
			time.sleep(5)

	GPIO.cleanup()
