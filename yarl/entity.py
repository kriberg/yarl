from __future__ import annotations

import copy
from typing import TYPE_CHECKING, TypeVar

from .render_order import RenderOrder
from .types import RGB

if TYPE_CHECKING:
    from .components.ai import BaseAI
    from .components.fighter import Fighter
    from .game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity(object):
    parent: GameMap

    def __init__(
        self,
        parent: GameMap | None = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: RGB = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.char: str = char
        self.color: RGB = color
        self.name: str = name
        self.blocks_movement: bool = blocks_movement
        self.render_order: RenderOrder = render_order
        if parent:
            self.parent = parent
            parent.entities.add(self)

    @property
    def game_map(self) -> GameMap:
        return self.parent.game_map

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def spawn(self: T, game_map: GameMap, x: int, y: int) -> T:
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = game_map
        game_map.entities.add(clone)
        return clone

    def place(self, x: int, y: int, game_map: GameMap | None = None) -> None:
        self.x = x
        self.y = y
        if game_map:
            if hasattr(self, "parent"):
                if self.parent is self.game_map:
                    self.game_map.entites.remove(self)
            self.parent = game_map
            game_map.entities.add(self)


class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: RGB = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: type[BaseAI],
        fighter: Fighter,
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )
        self.ai: BaseAI | None = ai_cls(self)
        self.fighter: Fighter = fighter
        self.fighter.parent = self

    @property
    def is_alive(self) -> bool:
        return bool(self.ai)
