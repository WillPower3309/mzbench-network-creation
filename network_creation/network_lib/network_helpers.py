# coding=utf-8

#   ███╗   ██╗███████╗████████╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗
#   ████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝
#   ██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║██║   ██║██████╔╝█████╔╝
#   ██║╚██╗██║██╔══╝     ██║   ██║███╗██║██║   ██║██╔══██╗██╔═██╗
#   ██║ ╚████║███████╗   ██║   ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗
#   ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

#   ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗ ███████╗
#   ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗██╔════╝
#   ███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝███████╗
#   ██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗╚════██║
#   ██║  ██║███████╗███████╗██║     ███████╗██║  ██║███████║
#   ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝


####################################
# Imports
####################################


import requests
import random


####################################
# Function Declarations
####################################


def create_network(domain, gatekeeper_key=None):
    # Can make a MAC address, range can be from 00 to FF
    num = random.randint(0, 10000000000)
    myAddress = MacAddress(mac=num)
    myNetwork = CoreNetworkMock(
        myAddress.address(), "", server=domain, gk_key=gatekeeper_key, ssl=True
    )

    # register the network myself
    myNetworkModel = CoreNetworkMock.core_create_dummy_network_model(myAddress)
    CoreNetworkMock.gatekeeper_register_network(myNetwork, myNetworkModel)

    # Let the class do the work for me and return the information
    GatekeeperResponse = myNetwork.core_populate_network()
    return GatekeeperResponse


####################################
# CoreNetworkMock Class Definition
####################################


class CoreNetworkMock:
    def __init__(
            self,
            mac,
            time,
            server,
            url=None,
            mqtt=None,
            mqtt_port=1883,
            client_id=None,
            ssl=None,
            user=None,
            password=None,
            gk_key=None,
    ):
        self.macAddress = MacAddress()
        self.macAddress.set_mac(mac)
        self.time = time
        self.server = server
        self.errors = 0
        self.user = user
        self.password = password

        self.network_id = None
        self.guardian_id = None
        self.guardian_type = None

        if url is None and ssl is None:
            if not gk_key:
                self.url = "http://mns." + server + "/gatekeeper"
            else:
                self.url = (
                        "http://gatekeeper."
                        + server
                        + "/?access_token="
                        + gk_key
                )
        elif url is None and ssl is not None:
            if not gk_key:
                self.url = "https://mns." + server + "/gatekeeper"
            else:
                self.url = (
                        "https://gatekeeper."
                        + server
                        + "/?access_token="
                        + gk_key
                )
        else:
            self.url = url
        if mqtt is None:
            self.mqtt = "mqtt." + server
        self.mqtt_port = mqtt_port
        if client_id is None:
            self.client_id = "sys-" + self.macAddress.address_without_colon()
        else:
            self.client_id = client_id

    def gatekeeper_send_status_report(self, status):
        # Send a status report to gatekeeper.
        # This returns the request result.
        # status = create_radar_status_report(network, node)
        payload = {
            "radar_status": status,
            "factory_reset": False,
            "master_failed": False,
            "location_id": self.macAddress.address(),
        }
        r = requests.post(self.url, json=payload)
        return r

    def gatekeeper_register_network(self, network):
        # Register a new (or existing) network by publishing radar status reports to gatekeeper.
        results = []
        for node in network["nodes"]:
            if node["role"] not in ["master", "peer"]:
                continue
            status = self.create_radar_status_report(network, node)
            root = self.gatekeeper_send_status_report(status)
            results.append(root)
            if root.status_code != 200:
                print(root.__dict__)
                raise Exception("Response Code %s: Failed to register Root node with gatekeeper." % root.status_code)
        return results

    def mac_address(self):
        return self.macAddress.address()

    def core_populate_network(self):
        # Create a dummy network model using the given mac prefix string
        network = self.core_create_dummy_network_model(self.macAddress)
        # Register the network with gatekeeper
        results = self.gatekeeper_register_network(network)
        master_cred = results[0].json()
        self.network_id = master_cred["local_config"]["guardian_mqtt"]["network_id"]
        guardian_config = master_cred["local_config"]["guardian_mqtt"]
        # Extract MQTT client connection information from the gatekeeper result for the master.
        self.client_id = guardian_config["guardian_id"]
        self.user = "device"
        self.password = guardian_config["mqToken"]
        self.mqtt = guardian_config["mqServer"]
        self.mqtt_port = guardian_config["mqPort"]
        self.guardian_id = guardian_config["guardian_id"]
        self.guardian_type = guardian_config["mqType"]

        response_code = results[0].status_code
        full_resp = results[0].json()
        results = {
            "network_id": self.network_id,
            "guardian_id": self.guardian_id,
            "guardian_type": self.guardian_type,
            "response_code": response_code,
            "full_results": full_resp,
            "network": network,
            "mqtt_token": guardian_config["mqToken"],
        }
        return results

    @staticmethod
    def mac_to_linkstr(mac):
        return mac.replace(":", "")[-6:]

    @staticmethod
    def core_create_dummy_network_model(mac_address):
        # Define a 3-node mesh network, where one acts as the gateway.
        network = {
            # External IP assigned to the master wan0 ethernet interface.
            "ip": "10.0.0.0",
            # Gateway mac and IP address
            "gateway": {"mac": "ff:00:00:00:00:00", "ip": "10.0.0.0"},
            "nodes": [
                {
                    # Master node
                    "role": "master",
                    "mesh_mac": mac_address.address(),
                    "eth_mac": mac_address.offset(1),
                    "wlan_2ghz_mac": mac_address.offset(2),
                    "wlan_5ghz_mac": mac_address.offset(3),
                    "peers": [1, 2, 3],
                },
                {
                    # Peer node 1
                    "role": "peer",
                    "mesh_mac": mac_address.offset("10"),
                    "eth_mac": mac_address.offset("11"),
                    "wlan_2ghz_mac": mac_address.offset("12"),
                    "wlan_5ghz_mac": mac_address.offset("13"),
                    "peers": [0, 2, 4],
                },
                {
                    # Peer node 2
                    "role": "peer",
                    "mesh_mac": mac_address.offset("20"),
                    "eth_mac": mac_address.offset("21"),
                    "wlan_2ghz_mac": mac_address.offset("22"),
                    "wlan_5ghz_mac": mac_address.offset("23"),
                    "peers": [0, 1, 5],
                },
                {
                    # Leaf node 1 (connected to Master)
                    "role": "leaf",
                    "mesh_mac": mac_address.offset("30"),
                    "peers": [0],
                },
                {
                    # Leaf node 2 (connected to Peer node 1)
                    "role": "leaf",
                    "mesh_mac": mac_address.offset("40"),
                    "peers": [1],
                },
                {
                    # Leaf node 3 (connected to Peer node 2)
                    "role": "leaf",
                    "mesh_mac": mac_address.offset("50"),
                    "peers": [2],
                },
            ],
        }
        return network

    @staticmethod
    def create_guardian_status_report(network, time_stamp, guardian_id, network_id, last_motion):
        radar_reports = []
        for node in network["nodes"]:
            if node["role"] not in ["master", "peer"]:
                continue
            radar_reports.append(
                CoreNetworkMock.create_radar_status_report(network, node)
            )

        report = {
            "ts": time_stamp,
            "guardian_id": guardian_id,
            "network_id": network_id,
            "radars": radar_reports,
            "last_motion": last_motion,
        }
        return report

    @staticmethod
    def create_radar_status_report(network, node):
        # Create a dummy-status block for a given network node, such
        # that we can get a valid response from gatekeeper with it.

        # Master node must be first one
        master_node = network["nodes"][0]

        # Create empty status report
        status = {
            "deviceId": "test-" + node["eth_mac"].replace(":", ""),
            "ts": 0.0,
            "interfaces": [],
            "links": [],
            "ap_bssid_2ghz": node["wlan_2ghz_mac"],
            "ap_bssid_5ghz": node["wlan_5ghz_mac"],
            "mesh_bssid": node["mesh_mac"],
            "gateway_bssid": master_node["mesh_mac"],
            "root_mode": 1,
        }

        # Override gateway bssid for master node:
        if node == master_node:
            status["gateway_bssid"] = network["gateway"]["mac"]
            status["root_mode"] = 2

        # Add wan0 ethernet interface with default gateway,
        # but only set its' type to ETHERNET if this is the master.
        if node == master_node:
            if_type = "ETHERNET"
        else:
            if_type = "BRIDGE"

        interface = {
            "name": "wan0",
            "type": if_type,
            "mac": node["eth_mac"],
            "ip": "10.22.22.1",
            "routes": [{"dst": "0.0.0.0"}],
        }
        status["interfaces"].append(interface)

        # Populate link list for all local peers
        # This is what is actually used to form the network.
        for peer_id in node["peers"]:
            peer_node = network["nodes"][peer_id]

            link_entry = {"mac": peer_node["mesh_mac"], "peer_type": "7"}

            if peer_node["role"] == "leaf":
                link_entry["peer_type"] = "2"

            status["links"].append(link_entry)
        return status


####################################
# MacAddress Class Definition
####################################


class MacAddress:
    def __init__(self, mac=0):
        self.number = 0
        self.set_mac(mac)

    def set_new_mac(self, header=0, start=1):
        header = int(str(header), 16)
        start = int(str(start), 16)
        self.number = (header * (16 ** 10)) + (start * (16 ** 6))

    def set_mac(self, mac):
        if isinstance(mac, str):
            self.number = self.mac_address_to_number(mac)
        else:
            self.number = mac

    def address(self):
        return self.convert_int_to_mac(self.number)

    def address_without_colon(self):
        return "{:012x}".format(self.number)

    def __repr__(self):
        return self.convert_int_to_mac(self.number)

    def number(self):
        return self.number

    def increment(self, step=1):
        self.number += step

    def offset(self, step):
        return self.convert_int_to_mac(self.add_to_mac_address(self.number, step))

    def increment_mac_section(self, section_to_increment=1):
        self.number += 1 * 16 ** ((section_to_increment * 2) - 2)

    @staticmethod
    def add_to_mac_address(mac, step):
        if isinstance(step, str):
            step = MacAddress.mac_address_to_number(step)
        if isinstance(mac, str):
            return MacAddress.convert_int_to_mac(MacAddress.mac_address_to_number(mac) + step)
        else:
            return mac + step

    @staticmethod
    def mac_address_to_number(mac):
        mac = mac.replace(":", "")
        return int(str(mac), 16)

    @staticmethod
    def convert_int_to_mac(mac):
        return "%02X:%02X:%02X:%02X:%02X:%02X" % (
            (mac >> 40) & 0xFF,
            (mac >> 32) & 0xFF,
            (mac >> 24) & 0xFF,
            (mac >> 16) & 0xFF,
            (mac >> 8) & 0xFF,
            (mac >> 0) & 0xFF
        )
