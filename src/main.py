#!/usr/bin/python
# coding: utf-8

# Example of using the MQTT client class to subscribe to a feed and print out
# any changes made to the feed.  Edit the variables below to configure the key,
# username, and feed to subscribe to for changes.

# Import standard python modules.
import sys
import os
import time
import RPi.GPIO as GPIO

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

FEED_ID = 'fireplace-burner-status'
TLC5916_LATCH = 17
TLC5916_CLK   = 27
TLC5916_SDI   = 22

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID))
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(FEED_ID)

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO! Reconnecting…')
    time.sleep(1)
    client.connect()

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received value: {1}'.format(feed_id, payload))
    burnerBit = GPIO.LOW
    if payload == 'OFF':
        burnerBit = GPIO.LOW
    elif payload == 'ON':
        burnerBit = GPIO.HIGH
    GPIO.output(18, burnerBit)
    for index in xrange(8):
        sendLEDBit(burnerBit)
        time.sleep(0.0001)
    GPIO.output(TLC5916_CLK, GPIO.LOW)
    time.sleep(0.0001)
    GPIO.output(TLC5916_LATCH, GPIO.HIGH)
    time.sleep(0.0001)
    GPIO.output(TLC5916_LATCH, GPIO.LOW)

def sendLEDBit(bitValue):
    GPIO.output(TLC5916_CLK, GPIO.LOW)
    time.sleep(0.0001)
    GPIO.output(TLC5916_SDI, bitValue)
    GPIO.output(TLC5916_CLK, GPIO.HIGH)
    
def my_callback(channel):  
    print "Rising edge detected on port channel {channel}" 

# Create an MQTT client instance.
client = MQTTClient(os.environ.get('AIO_USERNAME'), os.environ.get('AIO_KEY'))

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(TLC5916_SDI, GPIO.OUT)
GPIO.setup(TLC5916_CLK, GPIO.OUT)
GPIO.setup(TLC5916_LATCH, GPIO.OUT)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
GPIO.output(18, GPIO.LOW)

GPIO.add_event_detect(23, GPIO.RISING, callback=my_callback)  
GPIO.add_event_detect(24, GPIO.RISING, callback=my_callback)  

# Start a message loop that blocks forever waiting for MQTT messages to be
# received.  Note there are other options for running the event loop like doing
# so in a background thread--see the mqtt_client.py example to learn more.
client.loop_blocking()