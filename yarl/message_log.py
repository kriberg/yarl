import textwrap
from collections.abc import Generator, Reversible

import tcod

from . import colors
from .types import RGB


class Message(object):
    def __init__(self, text: str, fg: RGB) -> None:
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text


class MessageLog(object):
    def __init__(self) -> None:
        self.messages: list[Message] = []

    def add_message(
        self,
        text: str,
        fg: RGB = colors.WHITE,
        *,
        stack: bool = True,
    ) -> None:
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))

    def render(
        self,
        console: tcod.console.Console,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        self.render_messages(console, x, y, width, height, self.messages)

    @staticmethod
    def wrap(string: str, width: int) -> Generator[str]:
        for line in string.splitlines():
            yield from textwrap.wrap(line, width, expand_tabs=True)

    @classmethod
    def render_messages(
        cls,
        console: tcod.console.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ) -> None:
        y_offset = height - 1
        for message in reversed(messages):
            for line in reversed(list(cls.wrap(message.full_text, width))):
                _ = console.print(x=x, y=y + y_offset, text=line, fg=message.fg)
                y_offset -= 1
                if y_offset < 0:
                    return
