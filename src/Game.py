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

    def __init__(self, players: List[Player]):
        self.characters = set({Character(color) for color in colors})
        self.players = players

        self.character_cards = list(self.characters)
        self.active_cards = list()
        self.alibi_cards = self.character_cards.copy()

        self.fantom = choice(self.alibi_cards) # a modifié pour choisir le fantom

        self.alibi_cards.remove(self.fantom)
        self.alibi_cards.extend(['fantom'] * 3)

        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked,
            "characters": self.characters_display,
            # Todo: should be removed
            "character_cards": self.character_cards_display,
            "active character_cards": self.active_cards_display,
        }

    def actions(self, step):
        """
        phase = tour
        phase 1 : IFFI
        phase 2 : FIIF
        first phase : initially num_tour = 1, then 3, 5, etc.
        so the first player to play is (1+1)%2=0 (inspector)
        second phase : num_tour = 2, 4, 6, 8, etc.
        so the first player to play is (2+1)%2=1 (fantom)
        """
        first_player_in_phase = (self.num_tour + 1) % 2
        if first_player_in_phase == 0:
            shuffle(self.character_cards)
            self.active_cards = self.character_cards[:4]
        else:
            self.active_cards = self.character_cards[4:]

        # the characters should be able to use their power at each new round
        for card in self.active_cards:
            card.power_activated = False

        if (step > 3):
            self.players[first_player_in_phase].play(self)
        if (step > 2):
            self.players[1 - first_player_in_phase].play(self)
        if (step > 1):
            self.players[1 - first_player_in_phase].play(self)
        if (step > 0):
            self.players[first_player_in_phase].play(self)

    def fantom_scream(self):
        partition: List[Set[Character]] = [
            {p for p in self.characters if p.position == i} for i in range(10)]
        if len(partition[self.fantom.position]) == 1 \
                or self.fantom.position == self.shadow:
            logger.info("The fantom screams.")
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

    def tour(self, game_state, step):
        self.set_game_state(game_state)
        self.actions(step)
        self.fantom_scream()
        for p in self.characters:
            p.power = True
        self.num_tour += 1

    def update_game_state(self, player_role):
        """
            representation of the global state of the game.
        """
        self.characters_display = [character.display() for character in
                                   self.characters]
        # Todo: should be removed
        self.character_cards_display = [tile.display() for tile in
                                        self.character_cards]
        self.active_cards_display = [tile.display() for tile in
                                     self.active_cards]
        # update

        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked,
            "characters": self.characters_display,
            # Todo: should be removed
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
        self.active_cards_display = game_state["active"]
        self.game_state = game_state