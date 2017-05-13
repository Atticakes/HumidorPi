# HumidorPi
This is a DIY project to modify a cigar humidor and enable it to be "self monitoring" by using the following hardware: Raspberry Pi, Adafruit Sensor AM2302, Yepkit USB Smart Hub, Centrifugal Fan, and Ultrasonic Humidifier.<br>
With this the Raspberry Pi will receive real humidity readings from the AM2302 sensor, and based on set thresholds will send control commands via command line to the Yepkit USB Smart Hub (or YKUSH for short) to enable/disable power to the connected Centrifugal Fan & Ultrasonic Humidifier.<br>
All the while the Raspberry Pi will be reporting back to Initial State to allow for abroad status readings & history tracking.<br>
The control program will be written in Python and utilize shell commands in order to control the YKUSH unit.
