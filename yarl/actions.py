from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import Engine
    from .entity import Actor, Entity

from typing import override

from . import colors
from .types import Point


class Action(object):
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity: Actor = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine

    def perform(self) -> None:
        raise NotImplementedError()


class EscapeAction(Action):
    @override
    def perform(self) -> None:
        raise SystemExit()


class WaitAction(Action):
    @override
    def perform(self) -> None:
        pass


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int) -> None:
        super().__init__(entity)
        self.dx: int = dx
        self.dy: int = dy

    @property
    def dest_xy(self) -> Point:
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        return self.engine.game_map.get_block_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Actor | None:
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    @override
    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    @override
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            return
        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = colors.PLAYER_ATK
        else:
            attack_color = colors.ENEMY_ATK
        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} for no damage.", attack_color
            )


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
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
