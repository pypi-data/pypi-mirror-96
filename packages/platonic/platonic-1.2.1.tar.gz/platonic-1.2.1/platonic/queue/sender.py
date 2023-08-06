from abc import abstractmethod
from typing import Callable, Iterable

from platonic.cached_property import cached_property
from platonic.queue.base import BaseQueue
from platonic.queue.message import Message
from platonic.queue.types import InternalType, ValueType


class Sender(BaseQueue[ValueType]):
    """Send messages to a queue."""

    @cached_property
    def serialize_value(self) -> Callable[[ValueType], InternalType]:
        """Serialize a queue item into internal representation."""
        return self.typecasts[  # pragma: no cover
            self.value_type,
            self.internal_type,
        ]

    @abstractmethod
    def send(self, instance: ValueType) -> Message[ValueType]:
        """Push a message into the queue."""

    def send_many(self, iterable: Iterable[ValueType]) -> None:
        """Put multiple messages into the queue."""
        for instance in iterable:  # pragma: no cover
            self.send(instance)
