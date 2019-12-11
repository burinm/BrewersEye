#!/usr/bin/env python3

""" Base code taken from mathworks tutorial
        https://www.mathworks.com/help/thingspeak/use-raspberry-pi-board-that-runs-python-websockets-to-publish-to-a-channel.html

    This code was used for initial testing of Thingspeak,
    but was replaced by the "thingspeak" MQTT client
    in the final version
"""

from __future__ import print_function
import paho.mqtt.publish as publish

# The hostname of the ThingSpeak MQTT broker.
mqttHost = "mqtt.thingspeak.com"
tTransport = "websockets"
tPort = 80

# You can use any username.
mqttUsername = "TSMQTTRpiDemo"

# Your MQTT API key from Account > My Profile.
mqttAPIKey = "GPUY41FE3EO6KSCI"

# The ThingSpeak Channel ID.
# Replace <YOUR-CHANNEL-ID> with your channel ID.
channelID = "899531"

# The write API key for the channel.
# Replace <YOUR-CHANNEL-WRITEAPIKEY> with your write API key.
writeAPIKey = "MFFLVEF5SP8EA2PN"

# Create the topic string.
topic = "channels/" + channelID + "/publish/" + writeAPIKey

# Rasberry pi client Id
clientID = 'deadbeefSuperPro'


def updateChannel(inside: float,
                  outside: float,
                  bubbles: int):

    temperature1 = "{:.2f}".format(inside)
    temperature2 = "{:.2f}".format(outside)
    bubbles_field = str(bubbles)

    # build the payload string.
    payload = "field1=" + temperature1 + \
              "&field2=" + temperature2 + \
              "&field3=" + bubbles_field

    print("Sending to ThingSpeak: " + payload)

    # attempt to publish this data to the topic.
    try:
        publish.single(topic,
                       payload,
                       hostname=mqttHost,
                       transport=tTransport,
                       port=tPort,
                       auth={'username': mqttUsername, 'password': mqttAPIKey})

        print("success to host: ", mqttHost, " clientID= ", clientID)
    except:
        print("There was an error while publishing the data.")
