from datetime import time
from socket import *
import struct
from Configuration import *
# import getch #TODO: change to this in VS
import msvcrt

def recieveMessage():
    # try to get a server
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO : change to SO_REUSEPORT
    sock.bind(("", udp_port))
    message = None
    while message is None:
        try:
            sock.settimeout(0.5)
            message = sock.recvfrom(BUFFER_SIZE)
        except:
            continue
    return message

def connectTcp(addr, port_num):
    tcpIp, _ = addr
    # tcpIp="127.0.0.1"  # for check our server
    # portNum=2043
    # tcp socket
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.connect((tcpIp, port_num))
    tcp_socket.send(bytes(team_name3 + "\n", "utf-8"))
    data = tcp_socket.recv(BUFFER_SIZE).decode("utf-8")
    # the message that the server sent at the beginning of the game
    print(data)
    ## game state
    startPlaying(tcp_socket)

def startPlaying(tcp_socket):
    ## game state
    try:
        val = msvcrt.getch()
        tcp_socket.sendall(bytes(val, "utf-8"))
        msgFromServer = tcp_socket.recv(BUFFER_SIZE).decode("utf-8")
        print(msgFromServer)
    except:
        return

def getPort(receivedData):
    # check if message is correct type - if yes return port number else return None
    try:
        # print(struct.unpack("Ibh", receivedData))
        unPackMsg = struct.unpack(">Ibh", receivedData)
        if unPackMsg[0] != 2882395322 or unPackMsg[1] != 2 or unPackMsg[2] < 1024 or unPackMsg[2] > 32768:
            return None
    except:  # message format not good (needs to be "Ibh")
        return None
    return unPackMsg[2]

## Flow of Client
def startClient():
    print("Client started, listening for offer requests...")
    ## wait for offers
    while True:
        receivedData, address = recieveMessage()  # check buffer size
        # port_team = getPort(receivedData)
        print(f"Received offer from {address[0]}, attempting to connect...")
        ## state 2
        # print(struct.unpack("Ibh",receivedData))
        # verify what message
        portNum = getPort(receivedData)  # if message type is not good - returns None
        ## continue wait for others if None
        if portNum is None:
            continue
        ## attempting to connect TCP
        try:
            connectTcp(address, portNum)
        except:
            continue
        print("Server disconnected, listening for offer requests...")  ## continue to wait for offers

startClient()