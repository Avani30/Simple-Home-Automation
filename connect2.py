import pyrebase
import time
import RPi.GPIO as GPIO

data = None
cld = 0
db = None
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
pwm = None
allON = False

def switchStreamHandler(message):
	global data
	global cld
	global pwm
	global allON	

	print(message['path'])
	print(message['data'])
	
	

	if(cld == 1):
		val = message['data']
		if(val['label'] == 'All Appliances'):
			print('All appliances')
			if(val['switchedOn']):
				allON = True
				keys = data.keys()
				for key in keys:
					if(key!='switch0'):
						label = data[key]['label']
						changeSwitchState(label, data[key]['switchedOn'])
			else:
				allON = False
				keys = data.keys()
				for key in keys:
					if(key!='switch0'):
						label = data[key]['label']
						changeSwitchState(label, False)
		elif(allON):
			print('Switching')
			changeSwitchState(val['label'], val['switchedOn'])
			key = getKeyForLabel(val['label'])
			data[key]['switchedOn'] = val['switchedOn']
			print('Done')
		else:
			key = getKeyForLabel(val['label'])
			data[key]['switchedOn'] = val['switchedOn']

	else:
		cld = cld + 1
		data = message['data']
		if(data['switch0']['switchedOn']):
			allON = True
			keys = data.keys()
			for key in keys:
				if(key!='switch0'):
					label = data[key]['label']
					pin = getGPIOfor(label)
					GPIO.setup(pin, GPIO.OUT)
					if(pin==12):
						print('PWM set')
						pwm = GPIO.PWM(12, 50)
					changeSwitchState(label, data[key]['switchedOn'])
		else:
			allON = False
			keys = data.keys()
			for key in keys:
				if(key!='switch0'):
					label = data[key]['label']
					pin = getGPIOfor(label)
					GPIO.setup(pin, GPIO.OUT)
					if(pin==12):
						print('PWM set')
						pwm = GPIO.PWM(12, 50)
					changeSwitchState(label, False)

def changeSwitchState(label, state):
	pin = getGPIOfor(label)
	if (pin==12):
		if (state):
			pwm.start(2.5)
		else:
			pwm.start(7.5)
	else:
		if (state):
			GPIO.output(getGPIOfor(label), GPIO.HIGH)
		else:
			GPIO.output(getGPIOfor(label), GPIO.LOW)	
	
def getKeyForLabel(label):
	global data
	
	keys = data.keys()
	for key in keys:
		if (data[key]['label'] == label):
			return key

def getGPIOfor(label):
    return {
        'Bedroom Light': 21,
        'Washroom Light': 19,
        'Kitchen Light': 13,
        'Drawingroom Light': 15,
        'Television': 16,
        'Drawingroom Fan': 18,
        'Bedroom Fan': 11,
        'Garage': 12
    }.get(label, 21)

if __name__ == '__main__':
	try:
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
	
		switch_stream = db.child('Switches').stream(switchStreamHandler)
		while (True):
			time.sleep(2)
	except KeyboardInterrupt:
		pwm.stop()
		GPIO.cleanup()
