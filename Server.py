import queue
import selectors
import types

from Configuration import *
import concurrent
from concurrent.futures import thread
#from termcolor import colored
from socket import *
import threading
import operator
import random
import struct
import time

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
        self.tcpSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # TODO : change to SO_REUSEPORT
        # Binding TCP socket to their port
        self.tcpSocket.bind((dev_network, team_port))
        
        self.mutex = threading.Lock()
        self.players = []
        self.result = queue.Queue()
        self.sel = selectors.DefaultSelector()
        self.ans = 0

    def thread_send_Announcements(self):
        """
            This function calling to new thread that automatically
            sending out “offer” announcements via UDP broadcast
            once every second for playing in our server.
        """
        if len(self.players) < 2:
            threading.Timer(1.0, self.thread_send_Announcements).start()
            self.send_udp_broadcast_suggestion()
        
    def send_udp_broadcast_suggestion(self):
        """
            This function create and send the broadcast message
            that every thread need to sent
        """
        magic_cookie = int(0xabcddcba)
        message_type = int(0x2)
        packet = struct.pack(">Ibh", magic_cookie, message_type, team_port)
        print(Red, f"Server started, listening on IP address {dev_network}")
        self.udpSocket.sendto(packet, (dev_network, udp_port))

    def accept_wrapper(self, sock):
        """
        accepts connection requests from clients while still sending offer requests.
        """
        try:
            conn, address = sock.accept()  # Should be ready to read
            conn.setblocking(False)
            data = types.SimpleNamespace(addr=address, inb=b'', outb=b'')
            self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
        except:
            pass

    def waiting_for_clients(self):
        """
            This function is the first state of server.
            It's responding to request messages and new TCP connections.
            We stay in this state until two clients connect to server.
        """
        while len(self.players) < 2:
            try:
                client_socket, client_address = self.tcpSocket.accept()
                player_name = client_socket.recv(BUFFER_SIZE).decode("utf-8")
                player = (client_socket, client_address, player_name)
                self.players.append(player)
                client_socket.setblocking(False)#+++
                data = types.SimpleNamespace(addr=client_address, inb=b'', outb=b'')#+++
                self.sel.register(client_socket, selectors.EVENT_READ |selectors.EVENT_WRITE, data=data)#+++
            except:
                continue
                
        self.game_mode()
        
    def quick_math_generator(self):
        """
            This function generates a simple random math problem.
            :return: answer: list of [num1, operator, num2, result]
        """
        ops = { '+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv }
        op = random.choice(list(ops.keys()))
        x = random.randint(0, 20)
        y = random.randint(1, 20)  # We don't sample 0's to protect against divide-by-zero
        answer = [x, op, y, ops.get(op)(x, y)]
        return answer
 
    def game_mode(self):
        """
            This function is the second state of the server.
            It's collect characters from the network and decide the winner.
            We stay in this state until 10 seconds have passed or
            until one of the players has tried to answer the question
        """
        #time.sleep(10)
        
        # Continue to create a random question until its answer is between 0-9 and the number is integer.
        answer = self.quick_math_generator()
        while answer[3] < 0 or answer[3] > 9 or type(answer[3]) != int:
            answer = self.quick_math_generator()

        self.ans = answer[3]
        
        welcome_message = "Welcome to Quick Maths.\n"
        welcome_message += f"Player 1: {self.players[0][2]}"
        welcome_message += f"Player 2: {self.players[1][2]}"
        welcome_message += "==\n"
        welcome_message += "Please answer the following question as fast as you can:\n"
        welcome_message += f"How much is {answer[0]}{answer[1]}{answer[2]}?"
        
        # Send the welcoming message to all players
        for player in self.players:
            player[0].sendall(bytes(welcome_message, "utf-8"))

        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            for player in self.players:
                pool.submit(self.game_result, player[0], player[2])



        self.init_variables()
        print("Game over, sending out offer requests...")
        self.thread_send_Announcements()


    def game_result(self, player_socket, player_name):
        try:
            # Set timout to 10 seconds
            player_socket.settimeout(10)
            print("befor")
            player_answer = player_socket.recv(BUFFER_SIZE)
            print("afterr")
            print(player_answer)
            print("after print answer")
            self.result.put((player_answer, player_name))
            self.check_result(self.ans)

        except timeout:
            print("except")
            self.check_result(self.ans)
            return
            
    def check_result(self, actual_answer):
        player1 = self.players[0][2]
        player2 = self.players[1][2]
        if self.result.qsize() == 0:
            res = "Draw"
        else:
            player_name = self.result.get(block=False)
            
            if int(player_name[0]) == actual_answer:
                res = player_name[1]
            else:
                if player_name[1] == player1:
                    res = player2
                else:
                    res = player1
        
        game_result_message = "Game over!\n"
        game_result_message += f"The correct answer was {actual_answer}!\n\n"
        game_result_message += f"Congratulations to the winner: {res}"
        
        # Send to all players the game result message and close sockets
        for player in self.players:
            player[0].sendall(bytes(game_result_message, "utf-8"))
            player[0].close()
        
    def init_variables(self):
        self.players = []
        self.result = []
        self.ans = 0
        
if __name__ == '__main__':
    server = Server()
    server.tcpSocket.listen()
    server.thread_send_Announcements()
    server.waiting_for_clients()