import json
from typing import Tuple
from random import randint, choice
from src.globals import passages, colors, pink_passages, before, after, logger, mandatory_powers

class Player:
    num: int

    def __init__(self, n: int):
        self.num = n
        self.role: str = "inspector" if n == 0 else "fantom"

    def play(self, game, tree):
        self.tree = tree
        charact = self.select(game.active_cards, game.update_game_state(self.role))

        moved_character = self.activate_power(charact,
                                              game,
                                              before,
                                              game.update_game_state(self.role))

        self.move(charact,
                  moved_character,
                  game.blocked,
                  game.update_game_state(self.role),
                  game)

        self.activate_power(charact,
                            game,
                            after,
                            game.update_game_state(self.role))

    def select(self, active_cards, game_state):
        available_characters = [character.display()
                                for character in active_cards]
        question = {"question type": "select character",
                    "data": available_characters,
                    "game state": game_state}
        selected_character = self.tree.ask(self.num, question)

        if selected_character not in range(len(active_cards)):
            selected_character = randint(0, len(active_cards) - 1)

        perso = active_cards[selected_character]

        del active_cards[selected_character]
        return perso


    def get_adjacent_positions(self, charact, game):
        if charact.color == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[charact.position] if set([room, charact.position]) != set(game.blocked)]


    def get_adjacent_positions_from_position(self, position, charact, game):
        if charact.color == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[position] if set([room, position]) != set(game.blocked)]


    def activate_power(self, charact, game, activables, game_state):
        if not charact.power_activated and charact.color in activables:

            if charact.color in mandatory_powers:
                power_activation = 1

            else:
                question = {"question type": f"activate {charact.color} power",
                            "data": [0, 1],
                            "game state": game_state}
                power_activation = self.tree.ask(self.num, question)

                if power_activation == 1:
                    power_answer = "yes"
                else:
                    power_answer = "no"

            if power_activation:
                charact.power_activated = True

                if charact.color == "red":
                    draw = choice(game.alibi_cards)
                    game.alibi_cards.remove(draw)
                    if draw == "fantom":
                        game.position_carlotta += -1 if self.num == 0 else 1
                    elif self.num == 0:
                        draw.suspect = False

                if charact.color == "black":
                    for q in game.characters:
                        if q.position in self.get_adjacent_positions(charact, game):
                            q.position = charact.position

                if charact.color == "white":
                    for moved_character in game.characters:
                        if moved_character.position == charact.position and charact != moved_character:
                            available_positions = self.get_adjacent_positions(
                                charact, game)

                            character_to_move = str(
                                moved_character).split("-")[0]
                            question = {"question type": "white character power move " + character_to_move,
                                        "data": available_positions,
                                        "game state": game_state}
                            selected_index = self.tree.ask(self.num, question)

                            if selected_index not in range(len(available_positions)):
                                selected_position = choice(available_positions)

                            else:
                                selected_position = available_positions[selected_index]

                            moved_character.position = selected_position

                if charact.color == "purple":

                    available_characters = [q for q in game.characters if
                                            q.color != "purple"]

                    available_colors = [q.color for q in available_characters]

                    question = {"question type": "purple character power",
                                "data": available_colors,
                                "game state": game_state}
                    selected_index = self.tree.ask(self.num, question)

                    if selected_index not in range(len(colors)):
                        selected_character = choice(colors)

                    else:
                        selected_character = available_characters[selected_index]

                    charact.position, selected_character.position = selected_character.position, charact.position

                    return selected_character

                if charact.color == "brown":
                    available_characters = [q for q in game.characters if
                                            charact.position == q.position if
                                            q.color != "brown"]

                    available_colors = [q.color for q in available_characters]
                    if len(available_colors) > 0:
                        question = {"question type": "brown character power",
                                    "data": available_colors,
                                    "game state": game_state}
                        selected_index = self.tree.ask(self.num, question)

                        if selected_index not in range(len(colors)):
                            selected_character = choice(colors)
                        else:
                            selected_character = available_characters[selected_index]

                        return selected_character
                    else:
                        return None

                if charact.color == "grey":

                    available_rooms = [room for room in range(10) if room is
                                       not game.shadow]
                    question = {"question type": "grey character power",
                                "data": available_rooms,
                                "game state": game_state}
                    selected_index = self.tree.ask(self.num, question)

                    if selected_index not in range(len(available_rooms)):
                        selected_index = randint(0, len(available_rooms) - 1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    game.shadow = selected_room

                if charact.color == "blue":

                    available_rooms = [room for room in range(10)]
                    question = {"question type": "blue character power room",
                                "data": available_rooms,
                                "game state": game_state}
                    selected_index = self.tree.ask(self.num, question)

                    if selected_index not in range(len(available_rooms)):
                        selected_index = randint(0, len(available_rooms) - 1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    passages_work = passages[selected_room].copy()
                    available_exits = list(passages_work)
                    question = {"question type": "blue character power exit",
                                "data": available_exits,
                                "game state": game_state}
                    selected_index = self.tree.ask(self.num, question)

                    if selected_index not in range(len(available_exits)):
                        selected_exit = choice(passages_work)

                    else:
                        selected_exit = available_exits[selected_index]

                    game.blocked = tuple((selected_room, selected_exit))
            else:
                # if the power was not used
                return None

    def move(self, charact, moved_character, blocked, game_state, game):
        characters_in_room = [
            q for q in game.characters if q.position == charact.position]
        number_of_characters_in_room = len(characters_in_room)

        available_rooms = list()
        available_rooms.append(self.get_adjacent_positions(charact, game))
        for step in range(1, number_of_characters_in_room):
            next_rooms = list()
            for room in available_rooms[step-1]:
                next_rooms += self.get_adjacent_positions_from_position(room,
                                                                        charact,
                                                                        game)
            available_rooms.append(next_rooms)

        temp = list()
        for sublist in available_rooms:
            for room in sublist:
                temp.append(room)

        temp = set(temp)
        available_positions = list(temp)

        if charact.color == "purple" and charact.power_activated:
            pass
        else:
            question = {"question type": "select position",
                        "data": available_positions,
                        "game state": game_state}
            selected_index = self.tree.ask(self.num, question)

            if selected_index not in range(len(available_positions)):
                selected_position = choice(available_positions)

            else:
                selected_position = available_positions[selected_index]

            if charact.color == "brown" and charact.power_activated:
                charact.position = selected_position
                if moved_character:
                    moved_character.position = selected_position
            else:
                charact.position = selected_position
