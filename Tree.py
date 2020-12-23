import math

import Game

class Node:
    def __init__(self, wins, played, parent):
        self.parent = parent
        self.children = []
        self.wins = wins
        self.played = played

class Tree():
    def __init__(self):
        self.root = Node()
        self.game = Game()

    def new_simulation(self, characters, game_state):
        #reset Tree
        current = self.root
        sim_end = False

        #Create first childs
        self.root.wins = 0
        self.root.played = 0
        for i in range(characters):
            self.root.children.append(Node(0, 0, root))

        #Launch simulation
        while not sim_end:
            current = self.selection(self.root)
            current = self.expansion(current, characters, game_state)
    
    def choose_and_cut(self):
        best = 0.0
        best_node = 0
        for i in range(len(self.root.children)):
            if self.root.children[i].wins / self.root.children[i].played > best:
                best = self.root.children[i].wins / self.root.children[i].played
                best_node = i
        self.root = self.root.children[best_node] #cut
        return best_node

    #Exploit or Explore
    def selection(self):
        current = self.root
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
    def expansion(self, current, characters, game_state):
        self.game.tour(game_state, characters)
        #créer les noeuds en fonction des questions si la question n'a pas été explorée
        #if (len(node.children) == 0)
        #for i in range(len(data)):
        #node.children.append(Node(0, 0, root))

        #Simuler jusqu'à la fin du tour, avec un adversaire random si besoin + mémoriser les choix
        

    #Update values in the tree
    def backpropagation(self, win, leaf):
        i = leaf
        while (i != self.root):
            if (win):
                i.wins += 1
            i.played += 1
            i = i.parent