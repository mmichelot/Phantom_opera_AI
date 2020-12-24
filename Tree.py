import math
import random

from src.Game import Game

SIMULATION = 100

class Node:
    def __init__(self, wins, played, parent):
        self.parent = parent
        self.children = []
        self.wins = wins
        self.played = played

class Tree():
    def __init__(self, player):
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
            winner = 0
            if (innocents == 0 or (innocents == 1 and fantom_scream == True)):
                winner = 1
            self.backpropagation(winner == self.player, self.current_answer)
    
    def choose_and_cut(self):
        best = 0.0
        best_node = 0
        for i in range(len(self.root.children)):
            if self.root.children[i].played > 0 and self.root.children[i].wins / self.root.children[i].played > best:
                best = self.root.children[i].wins / self.root.children[i].played
                best_node = i
        if len(self.root.children == 0):
            print("Error")
        self.root = self.root.children[best_node] #cut
        return best_node

    #Exploit or Explore
    def selection(self, current):
        best = 0.0
        best_node = 0
        for i in range(len(current.children)):
            w = current.children[i].wins
            n = current.children[i].played
            c = math.sqrt(2)
            N = current.played
            if n == 0:
                res = 0
            else:
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
        while (i != self.root):
            if (win):
                i.wins += 1
            i.played += 1
            i = i.parent
    
    #Expansion
    #To answer the question asked by the simulation. Build the tree from here if player is my player.
    def ask(self, player, question):
        if (player == self.player):
            if (len(self.current_answer.children) == 0):
                for i in range(len(question['data'])):
                    self.current_answer.children.append(Node(0, 0, self.current_answer))
            answer, self.current_answer = self.selection(self.current_answer)
            return answer
        else:
            if (len(self.random_answer) > self.random_answer_index):
                return self.random_answer[self.random_answer_index]
            else:
                answer = random.randint(0, len(question['data'])-1)
                self.random_answer.append(answer)
                return answer