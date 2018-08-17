import pyrebase
import serial
import time
from multiprocessing import Process

db = None
ard = None

def fetch():
	global ard
	global db
	
	while(True):
		print('Reading')
		read = ard.readline().rstrip().decode('utf-8')
		print(read)
		rstr = read.split('-')
		print('Read')
		
		for substr in rstr:
			recv = substr.split(':')
			if(float(recv[1])<0.0):
				break
			maxVal = db.child('Sensors').child('sensor{0}'.format(recv[0])).child('max').get()
			minVal = db.child('Sensors').child('sensor{0}'.format(recv[0])).child('min').get()
			curVal = float(recv[1])

			print('Hope is still there {0}'.format(recv[0]))

			if (curVal>maxVal.val()):
				db.child('Sensors').child('sensor{0}'.format(recv[0])).update({'max':curVal})
			elif (curVal<minVal.val()):
				db.child('Sensors').child('sensor{0}'.format(recv[0])).update({'min':curVal})
			
			db.child('Sensors').child('sensor{0}'.format(recv[0])).update({'current':curVal})
			
			time.sleep(1)
		print('complete')
		
def messageStreamHandler(message):
	global ard
	global db
	
	if(message['data']):
		msg = db.child('AwayMessage').child('message').get()
		msg = msg.val().encode('ascii')
		print(msg)
		ard.write(msg)
	else:
		print('Msg deleted')
		ard.write('~'.encode('ascii'))


if __name__ == '__main__':
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
	
	ard = serial.Serial('/dev/ttyACM0', 9600)
	
	message_stream = db.child('AwayMessage').child('available').stream(messageStreamHandler)
	proc = Process(target=fetch)
	proc.start()
	proc.join()
