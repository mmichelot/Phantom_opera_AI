import json
from random import shuffle, randrange, choice
from typing import List, Set, Union, Tuple

from src.Character import Character
from src.Player import Player
from src.globals import logger, passages, colors


class Game:
    players: List[Player]
    position_carlotta: int
    exit: int
    num_tour: int
    shadow: int
    blocked: Tuple[int]
    characters: Set[Character]
    character_cards: List[Character]
    active_cards: List[Character]
    cards: List[Union[Character, str]]
    fantom: Character

    def __init__(self):
        self.players = [Player(0), Player(1)]

    def actions(self, tree):
        first_player_in_phase = (self.num_tour + 1) % 2

        for card in self.active_cards:
            card.power_activated = False

        if (len(self.active_cards) > 3):
            self.players[first_player_in_phase].play(self, tree)
        if (len(self.active_cards) > 2):
            self.players[1 - first_player_in_phase].play(self, tree)
        if (len(self.active_cards) > 1):
            self.players[1 - first_player_in_phase].play(self, tree)
        if (len(self.active_cards) > 0):
            self.players[first_player_in_phase].play(self, tree)

    def fantom_scream(self):
        screamed = False
        partition: List[Set[Character]] = [
            {p for p in self.characters if p.position == i} for i in range(10)]
        if len(partition[self.fantom.position]) == 1 \
                or self.fantom.position == self.shadow:
            logger.info("The fantom screams.")
            screamed = True
            self.position_carlotta += 1
            for room, chars in enumerate(partition):
                if len(chars) > 1 and room != self.shadow:
                    for p in chars:
                        p.suspect = False
        else:
            logger.info("the fantom does not scream.")
            for room, chars in enumerate(partition):
                if len(chars) == 1 or room == self.shadow:
                    for p in chars:
                        p.suspect = False
        self.position_carlotta += len(
            [p for p in self.characters if p.suspect])
        return screamed

    def get_number_of_suspects(self):
        return len([p for p in self.characters if p.suspect])

    def init_tour(self, game_state, active_cards):
        self.characters = []
        self.active_cards = []
        for character in game_state["characters"]:
            c = Character(character['color'])
            c.suspect = character['suspect']
            c.position = character['position']
            c.power = character['power']
            self.characters.append(c)
        for data in active_cards:
            for character in self.characters:
                if (character.color == data['color']):
                    self.active_cards.append(character)

        self.character_cards = list(self.characters)
        self.set_game_state(game_state)

    def tour(self, tree):
        self.actions(tree)

        screamed = self.fantom_scream()
        for p in self.characters:
            p.power = True
        self.num_tour += 1
        return screamed

    def update_game_state(self, player_role):
        self.characters_display = [character.display() for character in
                                   self.characters]
        self.character_cards_display = [tile.display() for tile in
                                        self.character_cards]
        self.active_cards_display = [tile.display() for tile in
                                     self.active_cards]
        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked,
            "characters": self.characters_display,
            "character_cards": self.character_cards_display,
            "active character_cards": self.active_cards_display
        }

        if player_role == "fantom":
            self.game_state["fantom"] = self.fantom.color

        return self.game_state


    def set_game_state(self, game_state):
        self.position_carlotta = game_state["position_carlotta"]
        self.exit = game_state["exit"]
        self.num_tour = game_state["num_tour"]
        self.shadow = game_state["shadow"]
        self.blocked = game_state["blocked"]
        self.characters_display = game_state["characters"]
        self.character_cards_display = game_state["character_cards"]
        self.active_cards_display = game_state["active character_cards"]
        self.game_state = game_state


        # set fantom
        self.alibi_cards = self.character_cards.copy()

        if "fantom" in game_state and game_state["fantom"]:
            for c in self.alibi_cards:
                if c.color == game_state["fantom"]:
                    self.fantom = c
        else:
            self.fantom = choice(self.alibi_cards)

        self.alibi_cards.remove(self.fantom)
        self.alibi_cards.extend(['fantom'] * 3)
