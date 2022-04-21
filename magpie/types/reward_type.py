from enum import Enum
from typing import List, Callable, Tuple, NamedTuple

from magpie.types.external_metrics import ExternalMetrics

INITIAL = "initial"
BEST = "best"
PREVIOUS = "previous"
CURRENT = "current"


class RewardInput(NamedTuple):
    initial: ExternalMetrics
    best: ExternalMetrics
    previous: ExternalMetrics
    current: ExternalMetrics


def args_extraction_function(args: List[str]) -> Tuple[Callable[[RewardInput, Callable], float], int, str]:
    """
    extract args from RewardInput according to args
    :param args:
    :return: a function which takes reward_input and a calculation as input and output fn(*_corresponding_args_value),
            len(args) and args_name
    """

    def _func(reward_input: RewardInput, fn):
        inputs = [getattr(reward_input, arg) for arg in args]
        return fn(*inputs)

    return _func, len(args), ",".join(args)


class RewardType(Enum):

    def __new__(cls, name, result: Callable[[RewardInput, Callable], float]):
        # value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj.func, obj.num_args_return, obj.description = result
        obj._name_ = f"reward_{name}"
        obj._value_ = obj._name_
        return obj

    def __str__(self):
        return self._name_.lower()

    def __repr__(self):
        return "<%s.%s: %s>" % (
            self.__class__.__name__, self._name_, self.description)

    @staticmethod
    def argparse(s):
        try:
            return RewardType[s.upper()]
        except KeyError:
            return s

    # Type 1A Reward utilizes moving average of previous metrics and current metrics
    REWARD_1A = ("1a", args_extraction_function([CURRENT]))
    # Type 2A Reward only utilizes previous and current metrics
    REWARD_2A = ("2a", args_extraction_function([PREVIOUS, CURRENT]))
    # Type 2B Reward only utilizes initial and current metrics
    REWARD_2B = ("2b", args_extraction_function([INITIAL, CURRENT]))
    # Type 2C Reward only utilizes best and current metrics
    REWARD_2C = ("2c", args_extraction_function([BEST, CURRENT]))
    # Type 3A Reward only utilizes initial, previous and current metrics
    REWARD_3A = ("3a", args_extraction_function([INITIAL, PREVIOUS, CURRENT]))
    # Type 3B Reward only utilizes initial, best and current metrics
    REWARD_3B = ("3b", args_extraction_function([INITIAL, BEST, CURRENT]))
    # Type 3C Reward only utilizes best, previous and current metrics
    REWARD_3C = ("3c", args_extraction_function([BEST, PREVIOUS, CURRENT]))
    # Type 4 Reward only utilizes initial, best, previous and current metrics
    REWARD_4 = ("4", args_extraction_function([INITIAL, BEST, PREVIOUS, CURRENT]))
