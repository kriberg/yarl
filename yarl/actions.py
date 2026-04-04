from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import Engine
    from .entity import Entity

from typing import override

from .types import Point


class Action(object):
    def __init__(self, entity: Entity) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine

    def perform(self) -> None:
        raise NotImplementedError()


class EscapeAction(Action):
    @override
    def perform(self) -> None:
        raise SystemExit()


class ActionWithDirection(Action):
    def __init__(self, entity: Entity, dx: int, dy: int) -> None:
        super().__init__(entity)
        self.dx: int = dx
        self.dy: int = dy

    @property
    def dest_xy(self) -> Point:
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        return self.engine.game_map.get_block_entity_at_location(*self.dest_xy)

    @override
    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    @override
    def perform(self) -> None:
        target = self.blocking_entity
        if not target:
            return
        print(f"You kick the {target.name}, much to its annoyance!")


class MovementAction(ActionWithDirection):
    @override
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        if self.engine.game_map.get_block_entity_at_location(dest_x, dest_y):
            return
        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    @override
    def perform(self) -> None:
        if self.blocking_entity:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
