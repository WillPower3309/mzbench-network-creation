#   ███╗   ██╗███████╗████████╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗
#   ████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝
#   ██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║██║   ██║██████╔╝█████╔╝
#   ██║╚██╗██║██╔══╝     ██║   ██║███╗██║██║   ██║██╔══██╗██╔═██╗
#   ██║ ╚████║███████╗   ██║   ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗
#   ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

#   ███╗   ███╗ ██████╗ ██████╗ ███████╗██╗
#   ████╗ ████║██╔═══██╗██╔══██╗██╔════╝██║
#   ██╔████╔██║██║   ██║██║  ██║█████╗  ██║
#   ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  ██║
#   ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗███████╗
#   ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝


####################################
# Imports
####################################


from .network_helpers import create_network


####################################
# NetworkModel Class Definition
####################################


class NetworkModel:
    def __init__(self, domain):
        network = create_network(domain)

        self._core_network_id = network['network_id']
        self._guardian_type = network['guardian_type']
        self._guardian_id = network['guardian_id']
        self._mqtt_creds = ('device', network['mqtt_token'])
        self._master_bssid = network['network']['nodes'][0]['wlan_5ghz_mac']
        self._network_schema = network['network']

    # ---------- Define Properties ---------- #
    @property
    def core_network_id(self):
        return self._core_network_id

    @property
    def guardian_type(self):
        return self._guardian_type

    @property
    def guardian_id(self):
        return self._guardian_id

    @property
    def mqtt_creds(self):
        return self._mqtt_creds

    @property
    def master_bssid(self):
        return self._master_bssid

    @property
    def network_schema(self):
        return self._network_schema
