from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entity import Entity
import numpy as np  # type: ignore
from tcod.console import Console

from . import tile_types


class GameMap(object):
    def __init__(self, width: int, height: int, entities: Iterable[Entity] = ()):
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
        self.visible = np.full((width, height), fill_value=False, order="F")
        self.explored = np.full((width, height), fill_value=False, order="F")
        self.entities: set[Entity] = set(entities)

    def get_block_entity_at_location(
        self, location_x: int, location_y: int
    ) -> Entity | None:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity
        return None

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )
        for entity in self.entities:
            if self.visible[entity.x, entity.y]:
                _ = console.print(entity.x, entity.y, entity.char, fg=entity.color)
