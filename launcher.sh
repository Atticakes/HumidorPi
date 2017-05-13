#!/bin/sh
#This is a simple launcher script that can be added to crontab to kick off the HumidorPi script on startup

cd /
cd home/pi/HumidorPi/
sleep 30
sudo python humidorpi.py
cd /
