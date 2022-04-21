from dataclasses import dataclass
from typing import List, Union

from magpie.types.external_metrics import ExternalMetrics
from magpie.types.knob import Knob


@dataclass
class TuneParameter:
    """
    tuning parameter value pair
    """
    name: Knob
    value: Union[int, float]

    def __str__(self):
        return f"{self.name.name}={self.value}"


@dataclass
class ScopedTuneParameters:
    scope: str
    parameters: List[TuneParameter]

    def __str__(self):
        list_str = ",".join([param.__str__() for param in self.parameters])
        return f"scope={self.scope},parameters={{ {list_str} }}"

    def __repr__(self):
        return self.__str__()

@dataclass
class DFSConfiguration:
    configuration: List[ScopedTuneParameters]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.configuration.__repr__()

    def __iter__(self):
        return self.configuration.__iter__()


@dataclass
class ConfigurationScorePair:
    configuration: DFSConfiguration
    score: ExternalMetrics

    def __lt__(self, other):
        if self.score is None:
            return True
        return self.score < other.score

    # def __str__(self):
    #     return self.__repr__()
    #
    # def __repr__(self):
    #     return f"configuration={self.configuration.configuration.__repr__()},score={self.score.__repr__()}"
