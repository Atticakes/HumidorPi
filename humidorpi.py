#! /usr/bin/python

##################################
###          Imports           ###
##################################

import json
import sys
import time
import datetime
import subprocess
import traceback
import Adafruit_DHT
from ISStreamer.Streamer import Streamer

##################################
###           Sensor           ###
##################################
DHT_TYPE = Adafruit_DHT.AM2302
DHT_PIN = 4

##################################
###          Variables         ###
##################################
streamer = Streamer(bucket_name="Humidor", bucket_key="bucket-key-goes-here", access_key="access-key-goes-here", buffer_size=200, debug_level=1)
FREQUENCY_SECONDS = 300
staleHumidity = None
staleTemp = None
statusControl = 0

##################################
###          CONTROL           ###
##################################
controlHumidity = 80

# Turn on the fan & turn off the humidifier
subprocess.call("ykushcmd -u 1", shell=True)
subprocess.call("ykushcmd -u 2", shell=True)

print('Logging sensor measurements to ISS every {0} seconds.'.format(FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')

print('entering main try')
try:
	print('entering main while loop')
	print(time.strftime('%a %H:%M:%S'))
	streamer.log("My Messages", "Starting Main Loop")
	time.sleep(5)
	while True:
		print('posting Monitoring Humidity')
		print('retrieving humidity')
		print(time.strftime('%a %H:%M:%S'))
		humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

		print('making sure there were readings')
		print(time.strftime('%a %H:%M:%S'))
		while humidity is None or temp is None:
			if statusControl != 3:
				streamer.log("Status", "No Reading")
				statusControl = 3
			print('failed to get readings')
			print(time.strftime('%a %H:%M:%S'))
			time.sleep(5)
			humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
		print('got readings')
		print(time.strftime('%a %H:%M:%S'))
		temp = round(temp * 1.8 + 32)
		humidity = round(humidity)
		if staleHumidity is None:
			if int(humidity) < int(controlHumidity):
				staleHumidity = int(humidity) + 1
			elif int(humidity) > int(controlHumidity):
				staleHumidity = int(humidity) - 1
			else:
				staleHumidity = humidity
		print('Temperature: {0:0.1f} F'.format(temp))
		print('Humidity:    {0:0.1f} %'.format(humidity))
		print(time.strftime('%a %H:%M:%S'))
		time.sleep(2)
		if humidity == staleHumidity:
			print('Humidity No Change - Skipping ISS Update')
			print(time.strftime('%a %H:%M:%S'))
			time.sleep(2)
		else:
			print('Change in Humidity')
			print(time.strftime('%a %H:%M:%S'))
			staleHumidity = humidity
			staleTemp = temp
			print('Sending to ISS')
			print(time.strftime('%a %H:%M:%S'))
			streamer.log("Humidity", int(humidity))
			streamer.log("Temperature", int(temp))
			time.sleep(10)
			print('Testing humidity')
			print(time.strftime('%a %H:%M:%S'))
			if int(humidity) < int(controlHumidity):
				print('Humidity less than control')
				print(time.strftime('%a %H:%M:%S'))
				subprocess.call("ykushcmd -u 1", shell=True)
				print('Turning on Fan')
				subprocess.call("ykushcmd -u 2", shell=True)
				print('Turning on Humidifier')
				if statusControl != 3:
					statusControl = 3
					streamer.log("Status", "Increasing Humidity")
					streamer.log("Fan", "ON")
					streamer.log("Humidifier", "ON")
				print('Testing complete')
				print(time.strftime('%a %H:%M:%S'))
			elif int(humidity) > int(controlHumidity):
				print('Humidity above control')
				print(time.strftime('%a %H:%M:%S'))
				subprocess.call("ykushcmd -u 1", shell=True)
				print('Turning on Fan')
				subprocess.call("ykushcmd -d 2", shell=True)
				print('Turning off Humidifier')
				if statusControl != 4:
					statusControl = 4
					streamer.log("Status", "Circulating Air")
	                                streamer.log("Fan", "ON")
	                                streamer.log("Humidifier", "OFF")
				print('Testing complete')
				print(time.strftime('%a %H:%M:%S'))
			else:
				print('Humidity at control')
				print(time.strftime('%a %H:%M:%S'))
				subprocess.call("ykushcmd -d 1", shell=True)
				print('Turning off Fan')
				subprocess.call("ykushcmd -d 2", shell=True)
				print('Turning off Humidifier')
				if statusControl != 5:
					statusControl = 5
					streamer.log("Status", "Idle")
					streamer.log("Fan", "OFF")
					streamer.log("Humidifier", "OFF")
				print('Testing complete')
				print(time.strftime('%a %H:%M:%S'))
		streamer.flush()
		streamer.log("My Messages", "Last Updated")
		if statusControl == 3:
			time.sleep(int(round(FREQUENCY_SECONDS / 2)))
		elif statusControl == 4:
			time.sleep(FREQUENCY_SECONDS)
		else:
			time.sleep(int(round(FREQUENCY_SECONDS * 2)))
except KeyboardInterrupt:
	print "Shutdown requested...exiting"
	streamer.log("My Messages", "Pi Shutting Down")
	streamer.log("Status", "Going Down")
	streamer.close()
except Exception:
	traceback.print_exc(file=sys.stdout)
sys.exit(0)
