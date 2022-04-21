import logging
from typing import List

import numpy as np
import tensorflow as tf
from devtools import pformat

from magpie.environment.dfs_environment import DFSEnvironment
from magpie.environment.reward import Reward
from magpie.environment.toy.toy_dfs_collector import ToyDFSCollector
from magpie.environment.toy.toy_dfs_controller import ToyDFSController
from magpie.types.external_metrics import ToyExternalMetrics
from magpie.types.knob import Knob
from magpie.types.performance_indicator import FloatPerformanceIndicator

np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)


class ToyEnvironment(DFSEnvironment):
    logger = logging.getLogger(__name__)

    def __init__(self, internal_pis: List[FloatPerformanceIndicator],
                 knobs: List[Knob], reward: Reward
                 , **kwargs):
        self.toy_state = np.array([-1, -1], dtype=np.float32)
        controller = ToyDFSController(self.toy_state)
        collector = ToyDFSCollector(self.toy_state)
        observation_time = 0
        super().__init__(internal_pis, ToyExternalMetrics, knobs, controller, collector, reward,
                         observation_time=observation_time, **kwargs)
        self.delay_after_initialization = 0

    def _initialization(self):
        self.toy_state[0] = 500
        self.toy_state[1] = 48

    def step_observe(self, new_parameters, current_state, current_external_metrics, reward):
        self.logger.info(
            f"current state {pformat(current_state)}, current_external metrics {pformat(current_external_metrics)}, reward={reward}")
        tf.summary.scalar('reward', reward)
        for name, value in current_external_metrics.get_all_metrics().items():
            tf.summary.scalar(f"tuned metric_{name}", value)
