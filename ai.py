import json
import socket
from abc import ABCMeta, abstractmethod

import protocol
from Tree import Tree

host = "localhost"
port = 12000
# HEADERSIZE = 10

class AI(object, metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, player):

        self.tree: Tree
        self.player = player #0 (inspector) or 1 (fantom)

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    @abstractmethod
    def log_answer(self, data, question, response_index):
        pass

    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]

        if question['question type'] == "select character":
            self.tree = Tree(self.player)
            self.tree.new_simulation(game_state, data)
        #print(question['question type'])
        #print("SERVER: " + str(data) + " : " + question['question type'])
        response_index = self.tree.choose_and_cut()
        if (question['question type'] != self.tree.root.question):
            print("[WARN] Question differs between server and simulation.\n> Answering to: " + question['question type'] + " (simulation: " + self.tree.root.question + ")" )
        # log
        self.log_answer(data, question, response_index)
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):

        self.connect()

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True
