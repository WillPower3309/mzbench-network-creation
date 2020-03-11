# coding=utf-8

#   ███╗   ███╗ ██████╗ ████████╗██╗ ██████╗ ███╗   ██╗
#   ████╗ ████║██╔═══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
#   ██╔████╔██║██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
#   ██║╚██╔╝██║██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
#   ██║ ╚═╝ ██║╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
#   ╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

#   ██████╗ ███████╗██████╗  ██████╗ ██████╗ ████████╗
#   ██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
#   ██████╔╝█████╗  ██████╔╝██║   ██║██████╔╝   ██║
#   ██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║██╔══██╗   ██║
#   ██║  ██║███████╗██║     ╚██████╔╝██║  ██║   ██║
#   ╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝


####################################
# Imports
####################################


import time
import random
import json

import paho.mqtt.client as mqtt


####################################
# Function Declarations
####################################


def send_motion_report(guardian_type, guardian_id, mqtt_creds, report_data, domain):
    # Report Matrix MQTT topic
    topic = "iot-2/type/%s/id/%s/evt/%s/fmt/json" % (
        guardian_type,
        guardian_id,
        "motion-matrix",
    )

    # MQTT URL
    mqtt_url = "mqtt.%s" % domain

    # On disconnect, break MQTT loop
    def on_disconnect(given_client):
        given_client.loop_stop()

    # Establish connection
    client = mqtt.Client(client_id=guardian_id)
    client.username_pw_set(mqtt_creds[0], mqtt_creds[1])
    client.connect(mqtt_url, 1883, 60)
    client.on_disconnect = on_disconnect
    client.loop()

    # Send data
    msg_info = client.publish(topic, json.dumps(report_data))

    # If message isn't published, return False, and fail test.
    if not msg_info.is_published():
        return False
    # If message is published, return True.
    if msg_info.is_published():
        return True


def send_report(network_model, domain):
    with open("network_lib/live_data.json") as json_file:
        motion_report_data = json.load(json_file)
    time.sleep(2)

    while 1:
        motion_report_data["ts"] = time.time()

        result = send_motion_report(
            network_model.guardian_type,
            network_model.guardian_id,
            network_model.mqtt_creds,
            motion_report_data,
            domain
        )

        if not result:
            print("ERROR: Report Not Sent")
            return
        else:
            print("Report sent")
        time.sleep(1)
