import json
import logging
import os
import random
import socket
import math
from logging.handlers import RotatingFileHandler

import protocol

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up fantom logging
"""
fantom_logger = logging.getLogger()
fantom_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/fantom.log"):
    os.remove("./logs/fantom.log")
file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
fantom_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
fantom_logger.addHandler(stream_handler)

class Tree:
    def __init__(self, wins, played, parent):
        self.parent = parent
        self.children = []
        self.wins = wins
        self.played = played
        self.game_state = None

#Exploit or Explore
def selection(root):
    current = root
    best = 0.0
    best_node = 0
    while (len(current.children) > 0): #while not leaf
        for i in range(len(current.children)):
            w = current.children[i].wins
            n = current.children[i].played
            c = math.sqrt(2)
            N = current.played
            res = (w / n) + (c * math.sqrt(math.log(N) / n))
            if (res > best):
                best = res
                best_node = i
        current = current.children[best_node]
    return current

#If not final, create childs (with the numbers of possibilities) and choose a child
#We know that the node is final if the simulation didn't ask for action anymore
#Launch backpropagation when node is final
def expansion(current):
    

#Update values in the tree
def backpropagation(win, current, root):
    i = current
    while (i != root):
        if (win):
            i.wins += 1
        i.played += 1
        i = i.parent

def new_simulation(root, characters):
    #reset Tree
    current = root
    sim_end = False

    #Create first childs
    root.wins = 0
    root.played = 0
    for i in range(characters):
        root.children.append(Tree(0, 0, root))

    #Launch simulation
    while not sim_end:
        current = selection(root)
        current = expansion(current)

def choose_in_tree(root):
    best = 0.0
    best_node = 0
    for i in range(len(root.children)):
        if root.children[i].wins / root.children[i].played > best:
            best = root.children[i].wins / root.children[i].played
            best_node = i
    return  root.children[best_node], best

class Player():

    def __init__(self):

        self.tree: Tree

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]

        if question['question type'] == "select character":
            self.tree = Tree()
            new_simulation(self.tree, len(data))
        self.tree, response_index = choose_in_tree(self.tree)
        # log
        fantom_logger.debug("|\n|")
        fantom_logger.debug("fantom answers")
        fantom_logger.debug(f"question type ----- {question['question type']}")
        fantom_logger.debug(f"data -------------- {data}")
        fantom_logger.debug(f"response index ---- {response_index}")
        fantom_logger.debug(f"response ---------- {data[response_index]}")
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


p = Player()

p.run()
