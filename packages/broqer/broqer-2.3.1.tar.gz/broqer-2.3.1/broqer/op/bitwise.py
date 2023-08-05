""" Enables accessing bits directly. Provides BitwiseCombineLatest to gather
publishers to bit indicies and evaluate a value from them.

map_bit builds a Publisher which is mapping to a specific bit on another
Publisher.
"""
from typing import Any, Dict  # noqa: F401

# pylint: disable=cyclic-import
from broqer import Publisher, Subscriber, NONE, SubscriptionDisposable
from broqer.op import build_map_factory

from broqer.operator import MultiOperator


class BitwiseCombineLatest(MultiOperator):
    """ Bitwise combine the latest emit of multiple publishers and emit the
    combination. If a publisher is not emitting or is not defined for a bit,
    the init value will be used.

    :param bit_publisher_mapping: dictionary with bit index as key and source
                                  publisher as value
    :param init: optional init value used for undefined bits (or initial state)
    """
    def __init__(self, publisher_bit_mapping: Dict, init: int = 0) -> None:
        MultiOperator.__init__(self, *publisher_bit_mapping)

        self._init = init
        self._missing = set(self._orginators)
        self._publisher_bit_mapping = publisher_bit_mapping

    def subscribe(self, subscriber: 'Subscriber',
                  prepend: bool = False) -> SubscriptionDisposable:
        disposable = MultiOperator.subscribe(self, subscriber, prepend)

        if self._missing:
            self._missing.clear()
            if self._state is NONE:
                Publisher.notify(self, self._init)
            else:
                Publisher.notify(self, self._state)

        return disposable

    def unsubscribe(self, subscriber: Subscriber) -> None:
        MultiOperator.unsubscribe(self, subscriber)
        if not self._subscriptions:
            self._missing.update(self._orginators)
            self._state = NONE

    def get(self):
        if self._subscriptions:
            return self._state

        state = self._init

        for publisher, bit_index in self._publisher_bit_mapping.items():
            value = publisher.get()

            if value is NONE:
                continue

            if value:
                state |= 1 << bit_index
            else:
                state &= ~(1 << bit_index)

        return state

    def emit(self, value: Any, who: Publisher) -> None:
        if all(who is not p for p in self._orginators):
            raise ValueError('Emit from non assigned publisher')

        # remove source publisher from ._missing
        self._missing.discard(who)

        # evaluate
        bit_index = self._publisher_bit_mapping[who]

        if self._state is NONE:
            self._state = self._init

        if value:
            self._state |= 1 << bit_index
        else:
            self._state &= ~(1 << bit_index)

        if self._missing:
            return None

        return Publisher.notify(self, self._state)


@build_map_factory()
def map_bit(bit_index, value):
    """ Provide value of a specific bit """
    return bool(value & (1 << bit_index))
