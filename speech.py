##!/usr/bin/env python
 
import sys
import json
import urllib
import subprocess
import pycurl
import StringIO
import os.path
import base64
import time
import RPi.GPIO as GPIO
import subprocess
from subprocess import Popen, PIPE, STDOUT

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
 
GPIO.setup(21,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)
pwm = GPIO.PWM(12, 50)

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

	
def changedByVC(pin, state):
	if (pin==12):
		if (state):
			pwm.start(2.5)
		else:
			pwm.start(7.5)
	else:
		if (state):
			GPIO.output(pin, GPIO.HIGH)
		else:
			GPIO.output(pin, GPIO.LOW)

def transcribe(duration):
 
	key ='AIzaSyA1j4JS2axP1LeoUGjBKkZiXnEsJLd7vxM'
	stt_url = 'https://speech.googleapis.com/v1beta1/speech:syncrecognize?key=' + key
	filename = 'test.flac'
 
	#Do nothing if audio is playing
	#------------------------------------
	if isAudioPlaying():
		#print time.strftime("%Y-%m-%d %H:%M:%S ")  + "Audio is playing"
		return ""
 
   
 
	#Record sound
	#----------------
 
	print ("listening ..")
	os.system('arecord -D plughw -f cd -c1 -t wav -d ' +str(duration) +' -q -r 16000 | flac - -s -f --best -o ' +filename)
	   
 
	#Check if the amplitude is high enough
	#---------------------------------------
	cmd = 'sox ' + filename + ' -n stat'
	p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	soxOutput = p.stdout.read()
	#print "Popen output" + soxOutput
 
   
	maxAmpStart = soxOutput.find("Maximum amplitude")+24
	maxAmpEnd = maxAmpStart + 7
   
	#print "Max Amp Start: " + str(maxAmpStart)
	#print "Max Amop Endp: " + str(maxAmpEnd)
 
	maxAmpValueText = soxOutput[maxAmpStart:maxAmpEnd]
   
   
	print ("Max Amp: " + maxAmpValueText)
 
	maxAmpValue = float(maxAmpValueText)
 
	if maxAmpValue < 0.1 :
		print ("No sound")
		#Exit if sound below minimum amplitude
		return ""  
   
 
	#Send sound  to Google Cloud Speech Api to interpret
	#----------------------------------------------------
   
	print (time.strftime("%Y-%m-%d %H:%M:%S ")  + "Sending to google api")
 
 
	# send the file to google speech api
	c = pycurl.Curl()
	c.setopt(pycurl.VERBOSE, 0)
	c.setopt(pycurl.URL, stt_url)
	fout = StringIO.StringIO()
	c.setopt(pycurl.WRITEFUNCTION, fout.write)
 
	c.setopt(pycurl.POST, 1)
	c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
 
	with open(filename, 'rb') as speech:
		# Base64 encode the binary audio file for inclusion in the JSON
			# request.
			speech_content = base64.b64encode(speech.read())
 
	jsonContentTemplate = """{
		'config': {
				'encoding':'FLAC',
				'sampleRate': 16000,
				'languageCode': 'en-GB',
			'speechContext': {
					'phrases': [
						'jarvis'
				],
			},
		},
		'audio': {
			'content':'XXX'
		}
	}"""
 
 
	jsonContent = jsonContentTemplate.replace("XXX",speech_content)
 
	#print jsonContent
 
	start = time.time()
 
	c.setopt(pycurl.POSTFIELDS, jsonContent)
	c.perform()
 
 
	#Extract text from returned message from Google
	#----------------------------------------------
	response_data = fout.getvalue()
 
 
	end = time.time()
	#print "Time to run:"
	#print(end - start)
 
 
	#print response_data
 
	c.close()
   
	start_loc = response_data.find("transcript")
	temp_str = response_data[start_loc + 14:]
	#print "temp_str: " + temp_str
	end_loc = temp_str.find("\""+",")
	final_result = temp_str[:end_loc]
	print "final_result: " + final_result
	return final_result
 
 
def isAudioPlaying():
   
	audioPlaying = False
 
	#Check processes using ps
	#---------------------------------------
	cmd = 'ps -C omxplayer,mplayer'
	lineCounter = 0
	p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
 
	for ln in p.stdout:
		lineCounter = lineCounter + 1
		if lineCounter > 1:
			audioPlaying = True
			break
 
	return audioPlaying ;
 
 
 
def listenForCommand():
   
	command  = transcribe(5)
   
	print (time.strftime("%Y-%m-%d %H:%M:%S ")  + "Command: " + command)
 
	success=True
 
	if command.lower().find("bed")>-1 and command.lower().find("light")>-1  and  command.lower().find("on")>-1   :
		print('turning bedroom lights on')
		changedByVC(getGPIOfor('Bedroom Light'),True)

	elif command.lower().find("bed")>-1 and command.lower().find("light")>-1  and  command.lower().find("off")>-1   :
		print('turning bedroom lights off')
		changedByVC(getGPIOfor('Bedroom Light'),False)

	elif command.lower().find("bed")>-1 and command.lower().find("fan")>-1  and  command.lower().find("on")>-1   :
		print('turning bedroom fan on') 
		changedByVC(getGPIOfor('Bedroom Fan'),True)

	elif command.lower().find("bed")>-1 and command.lower().find("fan")>-1  and  command.lower().find("off")>-1   :
		print('turning bedroom fan off')
		changedByVC(getGPIOfor('Bedroom Fan'),False)

	elif command.lower().find("wash")>-1 and command.lower().find("light")>-1  and  command.lower().find("on")>-1   :
		print('turning washroom light on')
		changedByVC(getGPIOfor('Washroom Light'),True)

	elif command.lower().find("wash")>-1 and command.lower().find("light")>-1  and  command.lower().find("off")>-1   :
		print('turning washroom light off')
		changedByVC(getGPIOfor('Washroom Light'),False)

	elif command.lower().find("kitchen")>-1 and command.lower().find("light")>-1  and  command.lower().find("on")>-1   :
		print('turning kitchen light on')
		changedByVC(getGPIOfor('Kitchen Light'),True)

	elif command.lower().find("kitchen")>-1 and command.lower().find("light")>-1  and  command.lower().find("off")>-1   :
		print('turning kitchen light off')
		changedByVC(getGPIOfor('Kitchen Light'),False)

	elif command.lower().find("drawing")>-1 and command.lower().find("light")>-1  and  command.lower().find("on")>-1   :
		print('turning drawingroom light on')
		changedByVC(getGPIOfor('Drawingroom Light'),True)

	elif command.lower().find("drawing")>-1 and command.lower().find("light")>-1  and  command.lower().find("off")>-1   :
		print('turning drawingroom light off')
		changedByVC(getGPIOfor('Drawingroom Light'),False)

	elif command.lower().find("television")>-1 and  command.lower().find("on")>-1   :
		print('turning TV on')
		changedByVC(getGPIOfor('Television'),True)

	elif command.lower().find("television")>-1 and  command.lower().find("off")>-1   :
		print('turning TV off')
		changedByVC(getGPIOfor('Television'),False)

	elif command.lower().find("drawing")>-1 and command.lower().find("fan")>-1  and  command.lower().find("on")>-1   :
		print('turning drawingroom fan on')
		changedByVC(getGPIOfor('Drawingroom Fan'),True)

	elif command.lower().find("drawing")>-1 and command.lower().find("fan")>-1  and  command.lower().find("off")>-1   :
		print('turning drawingroom fan off')
		changedByVC(getGPIOfor('Drawingroom Fan'),False)

	elif command.lower().find("open")>-1 and  command.lower().find("garage")>-1   :
		print('opening garage door')
		changedByVC(getGPIOfor('Garage'),True)

	elif command.lower().find("close")>-1 and  command.lower().find("garage")>-1   :
		print('closing garage door')
		changedByVC(getGPIOfor('Garage'),False)

	else:
		subprocess.call(["aplay", "i-dont-understand.wav"])
		success=False
 
	return success
 
 
 
print time.strftime("%Y-%m-%d %H:%M:%S ")  + "Launched spch.py"
 
try:
	while True:
		   
		sys.stdout.flush()
	   
		#Listen for trigger word
		print('listening for the trigger')
		spokenText = transcribe(2);
	   
		if len(spokenText) > 0:
			print (time.strftime("%Y-%m-%d %H:%M:%S ")  + "Trigger word: " + spokenText)
			triggerWordIndex  = spokenText.lower().find("oscar")
	
			if triggerWordIndex >-1:
				GPIO.output(26,GPIO.HIGH);
				#If trigger word found, listen for command
				success = listenForCommand()
				if not success:
					listenForCommand()
				GPIO.output(26,GPIO.LOW)
except KeyboardInterrupt:
	pwm.stop()
	GPIO.cleanup()