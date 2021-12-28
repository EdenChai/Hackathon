from Configuration import *
from datetime import time
from socket import *
import threading
import struct
import random

class Server:
    def __init__(self):
        
        # Initialize UDP socket
        self.udpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        # Enable port reusage so we will be able to run multiple clients and servers on single (host, port)
        self.udpSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # TODO : change to SO_REUSEPORT
        # Enable broadcasting mode
        self.udpSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        
        # Initialize TCP socket
        self.tcpSocket = socket(AF_INET, SOCK_STREAM)
        # Enable port reusage so we will be able to run multiple clients and servers on single (host, port)
        self.tcpSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        
        self.teams = []
        # self.hostName = gethostname()
        # self.hostIP = gethostbyname(gethostname())
        
    def thread_send_Announcements(self):
        """
        This function using by new process for approving terminate in 10 second.
        Its calling to new thread that send a broadcast invitation every 1 second for playing in our server
        """
        threading.Timer(1.0, self.thread_send_Announcements).start()
        # self.udpSocket.bind((dev_network, udp_port))
        # self.udpSocket.listen()
        self.send_udp_broadcast_suggestion()
        
    def send_udp_broadcast_suggestion(self):
        magic_cookie = int(0xabcddcba)
        message_type = int(0x2)
        packet = struct.pack(">Ibh", magic_cookie, message_type, team_port)
        print(f"Server started, listening on IP address {dev_network}", Yellow)
        # self.udpSocket.setblocking(False)
        self.udpSocket.sendto(packet, (dev_network, udp_port))   # send port to connect with TCP connection
        
    def waiting_for_clients(self):
        """
            this func is the first stage of server
            here server start to send offers to clients in net
            and listen for Tcp connections for Players that want to join
            this Func update Self.Teams the Clients that Registered
        """
        
        # threading.Thread(target=self.thread_send_Announcements).start()
        players = []
        while len(players) < 2:
            try:
                client_socket, client_address = self.tcpSocket.accept()
                player_name = client_socket.recv(BUFFER_SIZE).decode("utf-8").split('\n')
                player = (client_socket, client_address, player_name)
                players.append(player)
            except:
                continue
        self.game_mode(players)
        
        # print("Welcome to Quick Maths.")
        # print(f'Player {count_players}: {team_name}')
        # print("==")
    
    def game_mode(self, players):
        """
            This func gets a clients connected to game and check
            if his answer to the question is correct
        """
        start_time = time()
        
        welcome_message = "Welcome to Quick Maths.\n"
        welcome_message += f"Player 1: {players[0][2][0]}\n"
        welcome_message += f"Player 2: {players[1][2][0]}\n"
        welcome_message += "==\n"
        welcome_message += "Please answer the following question as fast as you can:\n"
        welcome_message += "How much is 2+2?"
        print(welcome_message)
        # counter = 0
        # start = time.time()
        # while time.time() - start < self.gameTime:
        #     try:
        #         client.settimeout(0.01)
        #         chartype = client.recv(self.bufferSize).decode("utf-8")
        #         counter += len(chartype)
        #     except:
        #         pass
        #
        # return counter
    
    # def random_funck(self):
    #     dic_of_func = { }
    #     x = random.randint(0, 9)
    #     y = 9 - x
    #     ans = x + y
    #     dic_of_func[f'{x}+{y}'] = ans
    #
    #     x = random.randint(0, 9)
    #     y = random.randint(0, x)
    #     ans = x - y
    #     dic_of_func[f'{x}-{y}?'] = ans
    #
    #     dic_of_func["8:2?"] = 4
    #     dic_of_func["6:3?"] = 2
    #     dic_of_func["9:3?"] = 3
    #     dic_of_func["4:2?"] = 2
    #     dic_of_func["4X2?"] = 8
    #     dic_of_func["3X2?"] = 6
    #     dic_of_func["3X3?"] = 9
    #
    #     rand = random.randint(0, len(dic_of_func - 1))
    #     return dic_of_func.items()[rand]


if __name__ == '__main__':
    server = Server()
    # con=False
    # while not con:
    #     try:
    server.tcpSocket.bind(("", 2046))
    #         con=True
    #     except:
    #         pass
    server.tcpSocket.listen()
    # while 1:
        # server.teams = []
        ## starting msg
        # print(colored(f"Server started,listening on IP address {server.d}",'red'))
        ## start sending udp offer annoucements via udp broadcast once every second
    server.thread_send_Announcements()
    server.waiting_for_clients()
