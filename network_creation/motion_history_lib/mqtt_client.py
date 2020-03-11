# coding=utf-8

#!/usr/bin/env python
#
# Description:  Simple MQTT client specifically for communicating with Halo Core.
#
# Author:       Trevor Pace
# Date Created: 3-1-2019


#   ███╗   ███╗ ██████╗ ████████╗████████╗     ██████╗██╗     ██╗███████╗███╗   ██╗████████╗
#   ████╗ ████║██╔═══██╗╚══██╔══╝╚══██╔══╝    ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝
#   ██╔████╔██║██║   ██║   ██║      ██║       ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   
#   ██║╚██╔╝██║██║▄▄ ██║   ██║      ██║       ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   
#   ██║ ╚═╝ ██║╚██████╔╝   ██║      ██║       ╚██████╗███████╗██║███████╗██║ ╚████║   ██║   
#   ╚═╝     ╚═╝ ╚══▀▀═╝    ╚═╝      ╚═╝        ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   


####################################
# Imports
####################################


import json
import paho.mqtt.client as mqtt
import time


####################################
# MqttClient Class Definition
####################################


class MqttClient:
    def __init__(self):
        self.cl = None

    def open(self, server, port, client_id, username, password):
        self.cl = mqtt.Client(client_id=client_id)
        self.cl.username_pw_set(username=username, password=password)
        self.cl.connect(server, port=port)
        self.cl.loop_start()

    def publish(self, device_type, device_id, event, data):
        # Blocking call to send a report to an MQTT client
        topic = "iot-2/type/%s/id/%s/evt/%s/fmt/json" % (device_type, device_id, event)

        check = 0
        msg_info = self.cl.publish(topic, json.dumps(data))
        if not msg_info.is_published():
            while not msg_info.is_published():
                if check == 0:
                    check = 0
                else:
                    time.sleep(1)
                check += 1
                if check > 30:
                    return False

    def close(self):
        self.cl.disconnect()
        self.cl.loop_stop()
        self.cl = None
