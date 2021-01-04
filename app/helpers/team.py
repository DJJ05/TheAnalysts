# -*- coding: utf-8 -*-

import random


class Team:
    def __init__(self, members, channels, current_message) -> None:
        self.members = members
        self.health = 20 * len(members)
        self.generals = random.sample(members, 3) if len(members) > 3 else members
        self.decrypted = 0
        self.points = 0
        self.researched = []
        self.channels = channels
        self.current_message = current_message

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'<Team members={str(self.members)} health={self.health} generals={str(self.generals)}>'

    def __int__(self) -> int:
        return self.health

    def __float__(self) -> float:
        return self.health

    def damage(self, damage) -> int:
        """Damages team health and returns new health"""
        self.health -= round(damage)
        return self.health

    def heal(self, heal) -> int:
        """Heals team health and returns new health"""
        self.health += round(heal)
        return self.health
