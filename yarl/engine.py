from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.context import Context
from tcod.map import compute_fov

from .input_handlers import EventHandler

if TYPE_CHECKING:
    from .entity import Entity
    from .game_map import GameMap


class Engine(object):
    game_map: GameMap

    def __init__(
        self,
        player: Entity,
    ) -> None:
        self.event_handler: EventHandler = EventHandler(self)
        self.player: Entity = player

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            print(f"The {entity.name} ponders life")

    def update_fov(self) -> None:
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)
        context.present(console)
        console.clear()
