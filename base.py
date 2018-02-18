# =======================
# load required libraries
# =======================

import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import pyrebase
from datetime import datetime


# ====================
# initialize variables
# ====================

# Firebase database to hold data for this whole project
firebase = pyrebase.initialize_app({
	"apiKey": "AIzaSyBBm8NcePI7FVG57L3tzl6psawP96pW45M",
	"authDomain": "alexaHomeSecurity.firebaseapp.com",
	"databaseURL": "https://alexahomesecurity.firebaseio.com",
	"storageBucket": "alexahomesecurity.appspot.com"
}).database()

# disable warnings sometimes printed when using SPI bus on Raspberry Pi
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
 
#initialize the radio module 
radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)
radio.setPayloadSize(1)
radio.setChannel(0x60) 										# must be the same for sensors and base station
radio.setDataRate(NRF24.BR_1MBPS)							# must be the same for sensors and base station
radio.setPALevel(NRF24.PA_MAX)
radio.setAutoAck(True)
radio.enableAckPayload()
radio.enableDynamicPayloads()
radio.openReadingPipe(1, [0xE0, 0xE0, 0xE0, 0xE0, 0xF2])	# set receiving address for this base station

armed = None		# initially set to None so first message from Firbase stream is acted on


# ====================================================
# handler function for incoming messages from firebase
# ====================================================

def handle(msg):
	global armed
	now = msg["data"]
	if now != armed:
		armed = now
		if now:
			print("Listening...")
			radio.startListening()					# start listening if /armed is True in Firebase
		else:
			print("Stopped!")
			radio.stopListening()					# stop listening if /armed is False in Firebase

stream = firebase.child("/armed").stream(handle) 	# create a stream to listen for changes for /armed in Firebase


# =========
# main loop
# =========

try:
	while(1):																				# run countinuously
		while not radio.available(0):														# wait for data to be available from radio
			time.sleep(1 / 100)																# sleep until data comes in
		packet = []
		radio.read(packet, radio.getDynamicPayloadSize())									# read the packet from the radio
		radio.flush_tx()																	# flush the transmitter so acknowledgement is sent
		event = {"time": datetime.now().strftime("%I:%M:%S%p"), "sensor": packet[0]}		# create an event object holding the current time, and which sensor detected the motion
		firebase.child("/events").push(event)												# add this event to the Firebase database
		print(event)
except KeyboardInterrupt as e:			# catch KeyboardInterrupt
	stream.close()						# close the stream and exit program
	print()
