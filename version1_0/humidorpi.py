#! /usr/bin/python

#This script is deprecated!!!!

##################################
###          Imports           ###
##################################

import json
import sys
import time
import datetime
import Adafruit_DHT
import os
import traceback
from ISStreamer.Streamer import Streamer

###################################
###           Sensor            ###
###################################
DHT_TYPE = Adafruit_DHT.AM2302
DHT_PIN = 4

###################################
###          Variables          ###
###################################
streamer = Streamer(bucket_name="Humidor", bucket_key="bucket-key-goes-here", access_key="access-key-goes-here")
FREQUENCY_SECONDS = 30
staleHumidity = None
staleTemp = None
fanControl = False
humControl = False
msgControl = 0

####################################
###           CONTROL            ###
####################################
controlHumidity = 80

# Turn off the fan & humidifier
os.system('ykushcmd -d 1')
os.system('ykushcmd -d 2')
streamer.log("Fan", "OFF")
streamer.log("Humidifier", "OFF")
streamer.log("Status", "Idle")
# DO NOT POWER OFF 3 = WiFi Module!

print('Logging sensor measurements to ISS every {0} seconds.'.format(FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')

try:
    while True:
        if msgControl != 0:
	    msgControl = 0
            streamer.log("My Messages", "Monitoring Humidity")
	elif msgControl == 0:
	    streamer.log("My Messages", "Monitoring Humidity")

        humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

        if humidity is None or temp is None:
            time.sleep(2)
	    continue
        temp = round(temp * 1.8 + 32)
        humidity = round(humidity)

        if staleHumidity is None or staleTemp is None:
            staleHumidity = humidity
	    staleTemp = temp
	    print('H & T = None')

        print('Temperature: {0:0.1f} F'.format(temp))
        print('Humidity:    {0:0.1f} %'.format(humidity))
   
        time.sleep(2)

        if humidity == staleHumidity:
    	    print('Humidity No Change - Skipping ISS Update')
	    streamer.log("Status", "Skipped")
            time.sleep(2)
        else:
	    staleHumidity = humidity
	    staleTemp = temp
            print('Sending to ISS')
	    if msgControl != 1:
	        msgControl = 1
	        streamer.log("My Messages", "Received Update")
	    streamer.log("Humidity", int(humidity))
	    streamer.log("Temperature", int(temp))
	    time.sleep(2)

        if int(humidity) < int(controlHumidity):
   	    if fanControl != True and humControl != True:
                os.system('ykushcmd -u 1')
                os.system('ykushcmd -u 2')
	        fanControl = True
	        humControl = True
	        streamer.log("Fan", "ON")
                streamer.log("Humidifier", "ON")
	        if msgControl != 2:
	            msgControl = 2
	            streamer.log("Status", "Increasing Humidity")
        elif int(humidity) > int(controlHumidity):
	    if fanControl != True and humControl != False:
                os.system('ykushcmd -u 1')
                os.system('ykushcmd -d 2')
	        fanControl = True
	        humControl = False
	        streamer.log("Fan", "ON")
                streamer.log("Humidifier", "OFF")
	        if msgControl != 3:
	            msgControl = 3
	            streamer.log("Status", "Circulating Air")
        else:
	    if fanControl != False and humControl != False:
                os.system('ykushcmd -d 1')
                os.system('ykushcmd -d 2')
	        fanControl = False
	        humControl = False
	        streamer.log("Fan", "OFF")
                streamer.log("Humidifier", "OFF")
	        if msgControl != 4:
	            msgControl = 4
	            streamer.log("Status", "Idle")
	streamer.close()
	time.sleep(FREQUENCY_SECONDS)

except KeyboardInterrupt:
	print "Shutdown requested...exiting"
	streamer.close()
except Exception:
	traceback.print_exc(file=sys.stdout)
sys.exit(0)
