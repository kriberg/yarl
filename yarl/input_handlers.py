from __future__ import annotations

from typing import TYPE_CHECKING, override

import tcod.event
import tcod.libtcodpy

from . import colors, exceptions
from .actions import (
    Action,
    BumpAction,
    DropItemAction,
    PickupAction,
    WaitAction,
)
from .types import Point

if TYPE_CHECKING:
    from .engine import Engine
    from .entity import Item


MOVE_KEYS: dict[int, Point] = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    # Vi keys.
    tcod.event.KeySym.H: (-1, 0),
    tcod.event.KeySym.J: (0, 1),
    tcod.event.KeySym.K: (0, -1),
    tcod.event.KeySym.L: (1, 0),
    tcod.event.KeySym.Y: (-1, -1),
    tcod.event.KeySym.U: (1, -1),
    tcod.event.KeySym.B: (-1, 1),
    tcod.event.KeySym.N: (1, 1),
}

WAIT_KEYS: set[int] = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
}


CURSOR_Y_KEYS: dict[int, int] = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

MODIFIER_KEYS: set[int] = {
    tcod.event.KeySym.LSHIFT,
    tcod.event.KeySym.RSHIFT,
    tcod.event.KeySym.LCTRL,
    tcod.event.KeySym.RCTRL,
    tcod.event.KeySym.LALT,
    tcod.event.KeySym.RALT,
}


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine) -> None:
        self.engine: Engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        self.handle_action(self.dispatch(event))

    def handle_action(self, action: Action | None) -> bool:
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], colors.IMPOSSIBLE)
            return False

        self.engine.handle_enemy_turns()
        self.engine.update_fov()
        return True

    @override
    def ev_quit(self, event: tcod.event.Quit) -> Action | None:
        raise SystemExit()

    @override
    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.console.Console) -> None:
        self.engine.render(console)


class MainGameEventHandler(EventHandler):
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)

    @override
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        action: Action | None = None

        key = event.sym
        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.KeySym.ESCAPE:
            raise SystemExit()
        elif key == tcod.event.KeySym.V:
            self.engine.event_handler = HistoryViewer(self.engine)
        elif key == tcod.event.KeySym.G:
            action = PickupAction(player)
        elif key == tcod.event.KeySym.I:
            self.engine.event_handler = InventoryActivateHandler(self.engine)
        elif key == tcod.event.KeySym.D:
            self.engine.event_handler = InventoryDropHandler(self.engine)

        return action


class GameOverEventHandler(EventHandler):
    @override
    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            raise SystemExit()


class HistoryViewer(EventHandler):
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    @override
    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        log_console = tcod.console.Console(console.width - 6, console.height - 6)
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        _ = log_console.print(
            x=0,
            y=0,
            text="┤Message history├",
            width=log_console.width,
            height=1,
            alignment=tcod.libtcodpy.CENTER,
        )
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    @override
    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0
            else:
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1
        else:
            self.engine.event_handler = MainGameEventHandler(self.engine)


class AskUserEventHandler(EventHandler):
    @override
    def handle_action(self, action: Action | None) -> bool:
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False

    @override
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        if event.sym in MODIFIER_KEYS:
            return None
        return self.on_exit()

    @override
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Action | None:
        return self.on_exit()

    def on_exit(self) -> Action | None:
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None


class InventoryEventHandler(AskUserEventHandler):
    TITLE: str = "<missing title>"

    @override
    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)
        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4
        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=colors.WHITE,
            bg=colors.BLACK,
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                _ = console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        else:
            _ = console.print(x + 1, y + 1, "(Empty)")

    @override
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | None:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.A

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", colors.INVALID)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Action | None:
        raise NotImplementedError()


class InventoryActivateHandler(InventoryEventHandler):
    TITLE = "Select an item to use"

    @override
    def on_item_selected(self, item: Item) -> Action | None:
        return item.consumable.get_action(self.engine.player)


class InventoryDropHandler(InventoryEventHandler):
    TITLE = "Select an item to drop"

    @override
    def on_item_selected(self, item: Item) -> Action | None:
        return DropItemAction(self.engine.player, item)
