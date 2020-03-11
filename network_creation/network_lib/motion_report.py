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
import json
import paho.mqtt.client as mqtt


####################################
# Function Declarations
####################################


def send_motion_report(network_model, report_data, domain):
    # Report Matrix MQTT topic
    topic = "iot-2/type/%s/id/%s/evt/%s/fmt/json" % (
        network_model.guardian_type,
        network_model.guardian_id,
        "motion-matrix",
    )

    # MQTT URL
    mqtt_url = "mqtt.%s" % domain

    # On disconnect, break MQTT loop
    def on_disconnect(given_client):
        given_client.loop_stop()

    # Establish connection
    client = mqtt.Client(client_id=network_model.guardian_id)
    client.username_pw_set(network_model.mqtt_creds[0], network_model.mqtt_creds[1])
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
    motion_report_data = {
        "ts": 0,
        "links": ["4C724010FD.4C72401124","4C72401124.4C724010FD"],
        "data": {
            "lraw": [0,0],
            "mkai": [0,0],
            "throughput": [1,1]
        },
        "loc": ["nomotion"],
        "interval": 500,
        "count": 1,
        "motion_tripped": 1,
        "last_motion": 1580935867.31,
        "motion_enabled": 0
    }

    while 1:
        motion_report_data["ts"] = time.time()
        result = send_motion_report(
            network_model,
            motion_report_data,
            domain
        )

        if not result:
            print("ERROR: Report Not Sent")
            return

        time.sleep(1)
