import multiprocessing
import sys
import threading
import time
import msvcrt
from socket import socket


class myThread (multiprocessing.Process):
    def __init__(self, threadID, name, my_socket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.my_socket = my_socket

    def run(self):
        client_answer = sys.stdin.readline(1)
        client_answer_bytes = bytes(client_answer, "utf-8")
        print(client_answer_bytes.decode())
        self.my_socket.send(client_answer_bytes)


