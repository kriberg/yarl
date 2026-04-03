from __future__ import annotations

import copy
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from .game_map import GameMap

RGB = tuple[int, int, int]
T = TypeVar("T", bound="Entity")


class Entity(object):
    def __init__(
        self,
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

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        gamemap.entities.add(clone)
        return clone
