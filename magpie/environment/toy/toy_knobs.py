from enum import Enum

from magpie.types.knob import IntKnob


class ToyKnobs(Enum):
    """
    toy knobs
    """
    KNOB1 = IntKnob(name="knob1", scope="earth", min=1, max=1000, default=10)
    KNOB2 = IntKnob(name="knob2", scope="earth", min=1, max=100, default=8)
