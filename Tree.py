import math
import random

from src.Game import Game

SIMULATION = 2000

def print_tree(node, index = 0, depth = 0):
    if (depth == 0):
        print("TREE:")
    current = node
    if (depth < 1):
        print(("---" * depth) + node.question + "[" + str(index) + "] : " + str(node.wins) + "/" + str(node.played))
    for i in range(len(node.children)):
        print_tree(node.children[i], i, depth + 1)

class Node:
    def __init__(self, wins, played, parent, question = ""):
        self.parent = parent
        self.children = []
        self.wins = wins
        self.played = played
        self.question = question
        self.innocents = -1

class Tree():
    def __init__(self, player):
        #print("NEW TREE")
        self.root = Node(0, 0, None)
        self.game = Game()
        self.player = player #0 (inspector) or 1 (fantom)
        self.current_answer = self.root
        self.random_answer = []
        self.random_answer_index = 0

    def new_simulation(self, game_state, characters):
        #Launch simulation
        for _ in range(SIMULATION):
            self.current_answer = self.root
            self.random_answer_index = 0
            self.game.init_tour(game_state, characters)
            suspects_before = self.game.get_number_of_suspects()
            fantom_scream = self.game.tour(self) #launch sim
            innocents = suspects_before - self.game.get_number_of_suspects()
            self.current_answer.innocents = innocents
            winner = 0
            if (innocents == 0 or (innocents == 1 and fantom_scream == True)):
                winner = 1
            self.backpropagation(winner == self.player, self.current_answer)
    
    def choose_and_cut(self):
        #print_tree(self.root)
        best = 0.0
        best_inno = -1
        best_node = 0
        for i in range(len(self.root.children)):
            if self.root.children[i].played > 0 and self.root.children[i].wins / self.root.children[i].played > best:
                best = self.root.children[i].wins / self.root.children[i].played
                best_node = i
        #In case no win is possible, we do our best
        if best == 0.0:
            for i in range(len(self.root.children)):
                #If i'm the inspector and I can do more innocents or I'm the fantom and I can do less innocents
                if best_inno < 0 or\
                    (self.player == 0 and self.root.innocents > best_inno) or\
                    (self.player == 1 and self.root.innocents < best_inno):
                    best_inno = self.root.innocents
                    best_node = i
        #print(self.root.children[best_node].question)
        try:
            self.root = self.root.children[best_node] #cut
        except IndexError:
            print("[CRITIC] Please make sure you start the inspector first, and then the fantom.")
            print("Exiting.")
            exit(1)
        #print("Answer: " + str(best_node))
        return best_node

    #Exploit or Explore
    def selection(self, current):
        best = 0.0
        best_node = 0
        for i in range(len(current.children)):
            w = current.children[i].wins
            n = current.children[i].played
            #c = math.sqrt(2)
            c = 2
            N = current.played
            if n == 0:
                return i, current.children[i]
            res = (w / n)
            if N != 0:
                res += (c * math.sqrt(math.log(N) / n))
            if (res > best):
                best = res
                best_node = i
        return best_node, current.children[best_node]
        #while (len(current.children) > 0): #while not leaf

    #Update values in the tree
    def backpropagation(self, win, leaf):
        i = leaf
        while (i != None):
            if (win):
                i.wins += 1
            i.played += 1
            if (i.parent != None):
                #If I'm the fantom and I can do less innocents
                if (self.player == 1 and (i.parent.innocents < 0 or i.parent.innocents < i.innocents)):
                    i.parent.innocents = i.innocents
                #If I'm the inspector and I can do more innocents
                elif (self.player == 0 and (i.parent.innocents < 0 or i.parent.innocents > i.innocents)):
                    i.parent.innocents = i.innocents
            i = i.parent
    
    #Expansion
    #To answer the question asked by the simulation. Build the tree from here if player is my player.
    def ask(self, player, question):
        if (player == self.player):
            #print("SIMU: " + str(question['data']) + " : " + question['question type'])
            if (len(self.current_answer.children) == 0):
                for i in range(len(question['data'])):
                    self.current_answer.children.append(Node(0, 0, self.current_answer, question['question type']))
            answer, self.current_answer = self.selection(self.current_answer)
            return answer
        else:
            if (len(self.random_answer) > self.random_answer_index):
                return self.random_answer[self.random_answer_index]
            else:
                answer = random.randint(0, len(question['data'])-1)
                self.random_answer.append(answer)
                return answer