from __future__ import annotations

from typing import TYPE_CHECKING, override

from .. import actions, colors, exceptions
from .base_component import BaseComponent
from .inventory import Inventory

if TYPE_CHECKING:
    from ..entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> actions.Action | None:
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        raise NotImplementedError()

    def consume(self) -> None:
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, Inventory):
            inventory.items.remove(entity)


class HealingConsumable(Consumable):
    def __init__(self, amount: int) -> None:
        self.amount: int = amount

    @override
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                colors.HEALTH_RECOVERED,
            )
            self.consume()
        else:
            raise exceptions.Impossible("Your health is already full.")
