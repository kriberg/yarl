from __future__ import annotations

import copy
from typing import TYPE_CHECKING, TypeVar

from .types import RGB

if TYPE_CHECKING:
    from .game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity(object):
    game_map: GameMap

    def __init__(
        self,
        game_map: GameMap | None = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: RGB = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.char: str = char
        self.color: RGB = color
        self.name = name
        self.blocks_movement = blocks_movement
        if game_map:
            self.game_map = game_map
            game_map.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def spawn(self: T, game_map: GameMap, x: int, y: int) -> T:
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.game_map = game_map
        game_map.entities.add(clone)
        return clone

    def place(self, x: int, y: int, game_map: GameMap | None = None) -> None:
        self.x = x
        self.y = y
        if game_map:
            if hasattr(self, "game_map"):
                self.game_map.entites.remove(self)
            self.game_map = game_map
            game_map.entities.add(self)
