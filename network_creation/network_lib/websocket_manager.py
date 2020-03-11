# coding=utf-8

#   ██╗    ██╗███████╗██████╗ ███████╗ ██████╗  ██████╗██╗  ██╗███████╗████████╗
#   ██║    ██║██╔════╝██╔══██╗██╔════╝██╔═══██╗██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝
#   ██║ █╗ ██║█████╗  ██████╔╝███████╗██║   ██║██║     █████╔╝ █████╗     ██║
#   ██║███╗██║██╔══╝  ██╔══██╗╚════██║██║   ██║██║     ██╔═██╗ ██╔══╝     ██║
#   ╚███╔███╔╝███████╗██████╔╝███████║╚██████╔╝╚██████╗██║  ██╗███████╗   ██║
#    ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝

#   ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗
#   ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗
#   ██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝
#   ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗
#   ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║  ██║
#   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝


####################################
# Imports
####################################


from lomond import WebSocket
from lomond.persist import persist

import time


####################################
# Class Declaration
####################################


class WebSocketManager(WebSocket):
    def __init__(self, ws_url, limit=5, start=time.time(), timeout=90):
        self.counter = 0
        self.message_array = []
        self.ws = WebSocket(ws_url)
        self.timeout = timeout
        self.start = start
        self.limit = limit
        self.did_timeout = False
        self.ready = False

    # Runs the websocket
    def run(self):
        for event in persist(self.ws):
            if event.name == "ready":
                self.ready = True
            elif event.name == "text":
                self.counter += 1
                self.message_array.append(event.text)
                if self.counter == self.limit:
                    time.sleep(3)
                    self.stop()
                    return
            if time.time() - self.start > self.timeout:
                self.did_timeout = True
                self.stop()
                return

    def stop(self):
        self.ws.close()
        return

    def ready_ws(self):
        return self.ready

    def get_counter(self):
        return self.counter

    def get_messages(self):
        return self.message_array

    def get_timeout(self):
        return self.did_timeout
