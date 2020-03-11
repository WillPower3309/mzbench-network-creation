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


def create_motionmatrix_report(network, time_stamp, interval, count, report_type=None):
    # Create a dummy motion matrix report

    if report_type == "matrix":
        data_key = "data"
    else:
        data_key = "motion"

    report = {
        "ts": time_stamp,
        "interval": interval * 100,
        "count": count,
        data_key: {"mkai": [], "throughput": []},
        "links": [],
    }
    # Generate link list combinations (using the mesh macs in the network).
    for i in range(len(network["nodes"]) - 1):
        for j in range(i + 1, len(network["nodes"])):
            src_mac = network["nodes"][i]["mesh_mac"]
            dest_mac = network["nodes"][j]["mesh_mac"]
            report["links"].append(
                src_mac.replace(":", "")[-6:]
                + "-"
                + dest_mac.replace(":", "")[-6:]
            )

    for _ in range(len(report["links"])):
        mkai = []
        throughput = []
        for x in range(report["count"]):
            mkai.extend([random.random()])
            throughput.extend([random.random()])
        report[data_key]["mkai"].append(mkai)
        report[data_key]["throughput"].append(throughput)
    return report


def send_motion_report(network_model, domain):
    # Report Matrix MQTT topic
    topic = "iot-2/type/%s/id/%s/evt/%s/fmt/json" % (
        network_model.guardian_type,
        network_model.guardian_id,
        "motion-matrix",
    )

    # MQTT URL
    mqtt_url = "mqtt.%s" % domain

    # Establish persistent connection
    client = mqtt.Client(client_id=network_model.guardian_id)
    client.username_pw_set(network_model.mqtt_creds[0], network_model.mqtt_creds[1])
    client.connect(mqtt_url, 1883, 60)
    client.loop_start()
    while True:
        msg_info = client.publish(topic, json.dumps(
            create_motionmatrix_report(
                network_model.network_schema, time.time(), 5, 1, "matrix"
            )
        ))
        if msg_info.rc != 0:
            print("ERROR: Failed to send mock live data")
        else:
            print("send report")

    client.loop_stop()
    client.disconnect()
