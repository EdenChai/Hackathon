import scapy.all as s

"""
Provide global configuration variables inside the typical 'config.py'
"""

# GLOBALS - CONSTANTS
udp_port = 13117
team_port = 2046

team_name = "Al Tagid Stam"
team_name2 = "Goal Nefesh"
team_name3 = "Busha Veherpa"

# dev_network = s.get_if_addr('eth1')
# test_network = s.get_if_addr('eth2')

BUFFER_SIZE = 1024

dev_network = "192.168.32.1"
# test_network = "172.99.0.255"

# COLORS
Black = '\u001b[30;1m'
Red = '\u001b[31;1m'
Green = '\u001b[32;1m'
Yellow = '\u001b[33;1m'
Blue = '\u001b[34;1m'
Magenta = '\u001b[35;1m'
Cyan = '\u001b[36;1m'
White = '\u001b[37;1m'
Bold = '\u001b[1m'
BgWhite = '\u001b[47;1m'
RESET = '\u001b[0m'