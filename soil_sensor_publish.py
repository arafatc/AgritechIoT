"""
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * This  File is modified by Arafat Chaghtai for educational purposes.
 * The author could be contacted at: arafatc@gmail.com for any clarifications.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 """
import time
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import datetime
import random
import math

# Define ENDPOINT, TOPIC, RELATIVE DIRECTORY for CERTIFICATE AND KEYS
ENDPOINT = "a2txamguxt48oa-ats.iot.us-east-1.amazonaws.com"
PATH_TO_CERT = r"E:\GreatLearning\Capstone\devices"
TOPIC_PUB = "iot/agritech"
TOPIC_SUB = "iot/wateralarm"


# AWS class to create number of objects (devices)
class AWS():
    # Constructor that accepts client id that works as device id and file names for different devices
    # This method will obviosuly be called while creating the instance
    # It will create the MQTT client for AWS using the credentials
    # Connect operation will make sure that connection is established between the device and AWS MQTT
    def __init__(self, client, certificate, private_key):
        self.client_id = client
        self.device_id = client
        self.cert_path = PATH_TO_CERT + "\\" + certificate
        self.pvt_key_path = PATH_TO_CERT + "\\" + private_key
        self.root_path = PATH_TO_CERT + "\\" + "AmazonRootCA1.pem"
        self.myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(self.client_id)
        self.myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
        self.myAWSIoTMQTTClient.configureCredentials(self.root_path, self.pvt_key_path, self.cert_path)
        self._connect()

    def _config(self):
        # AWSIoTMQTTClient connection configuration to avoid timeout
        self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect method to establish connection with AWS IoT core MQTT and subscribe to AWS IoT
    def _connect(self):
        self._config()
        self.myAWSIoTMQTTClient.connect()

    # This method will publish the data on MQTT
    # Before publishing we are confiuguring message to be published on MQTT

    # Custom MQTT message callback
    def _customCallback(self, client, userdata, message):
        print("Received a new message: ")
        print(message.payload)

    # Subscribe operation for each devices
    def subscribe(self):
        self.myAWSIoTMQTTClient.subscribe(TOPIC_SUB, 1, self._customCallback)
        print("Subscribed: " + self.client_id + " to the topic: " + TOPIC_SUB)

    # Publish operation for each devices
    def publish(self):
        # print('Begin Publish')
        # for i in range (10):
        consolidated_sensordata = {
            'deviceid': {},
            'timestamp': {},
            'Temperature': {},
            'MoistureSensor': {},
            'latitude': {},
            'longitude': {}}

        valueTemperature = float(round(random.uniform(18, 24), 1))
        valueMoisture = float(round(random.uniform(1, 100), 1))
        valuelatitude = math.acos(random.random() * 2 - 1)
        valuelongitude = random.random() * math.pi * 2

        consolidated_sensordata['deviceid'] = self.device_id
        consolidated_sensordata['timestamp'] = str(datetime.datetime.now())
        consolidated_sensordata['Temperature'] = valueTemperature
        consolidated_sensordata['MoistureSensor'] = valueMoisture
        consolidated_sensordata['latitude'] = valuelatitude
        consolidated_sensordata['longitude'] = valuelongitude

        messageJson = json.dumps(consolidated_sensordata)
        self.myAWSIoTMQTTClient.publish(TOPIC_PUB, messageJson, 1)
        print("Published: '" + json.dumps(consolidated_sensordata) + "' to the topic: " + TOPIC_PUB)

    # Disconect operation for each devices
    def disconnect(self):
        self.myAWSIoTMQTTClient.disconnect()


# Main method with actual objects and method calling to publish the data in MQTT
# Again this is a minimal example that can be extended to incopporate more devices
# Also there can be different method calls as well based on the devices and their working.
if __name__ == '__main__':
    # Create a list of Sensors
    soil_sensorlist = []
    water_sprinklerlist = []
    num_water_sprinkler = 1
    num_soil_sensor = 5

    for sensorIndex in range(num_water_sprinkler):
        prefix = "water_sprinkler" + "_" + str(sensorIndex + 1)
        postfix_cert = "-" + "certificate.pem.crt"
        postfix_key = "-" + "private.pem.key"

        dev_certificate = prefix + "\\" + prefix + postfix_cert
        dev_private_key = prefix + "\\" + prefix + postfix_key

        water_sprinklerlist.append(AWS(prefix, dev_certificate, dev_private_key))

    for sensor in water_sprinklerlist:
        sensor.subscribe()

    for sensorIndex in range(num_soil_sensor):
        prefix = "soil_sensor" + "_" + str(sensorIndex + 1)
        postfix_cert = "-" + "certificate.pem.crt"
        postfix_key = "-" + "private.pem.key"

        dev_certificate = prefix + "\\" + prefix + postfix_cert
        dev_private_key = prefix + "\\" + prefix + postfix_key

        soil_sensorlist.append(AWS(prefix, dev_certificate, dev_private_key))

    # Publish to the same topic in a loop forever, every 5 sec
    while True:
        try:
            for sensor in soil_sensorlist:
                sensor.publish()
            time.sleep(5)
        except KeyboardInterrupt:
            break
