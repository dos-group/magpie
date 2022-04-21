import logging
from typing import List

from magpie.environment.controller import DistributedDFSController
from magpie.environment.toy.toy_knobs import ToyKnobs
from magpie.types.dfs_configuration import ScopedTuneParameters
from magpie.types.knob import Knob


class ToyDFSController(DistributedDFSController):
    logger = logging.getLogger(__name__)

    def __init__(self, toy_state):
        self.toy_state = toy_state

    def _set_scope_params(self, scoped_parameters: ScopedTuneParameters, **kwargs):
        for tune_parameter in scoped_parameters.parameters:
            if tune_parameter.name is ToyKnobs.KNOB1.value:
                self.toy_state[0] = tune_parameter.value
            elif tune_parameter.name is ToyKnobs.KNOB2.value:
                self.toy_state[1] = tune_parameter.value
            else:
                raise NotImplementedError
        self.logger.debug(f"After controller setting, current knobs {self.toy_state[:2]}")

    def reset_params(self, tuned_params: List[Knob]):
        pass