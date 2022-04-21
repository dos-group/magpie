from unittest import TestCase

import tf_agents
from magpie.environment.toy_env.toy_env import ToyEnvironment
from magpie.environment.toy_env.toy_knobs import ToyKnobs
from magpie.environment.toy_env.toy_performance_indicators import ToyPerformanceIndicators as TPI

from magpie.environment.reward import SingleTuning2ProportionMetricsReward
from magpie.types.reward_type import RewardType
from magpie.utils import magpie_logging


class TestToyEnvironment(TestCase):
    def setUp(self) -> None:
        magpie_logging.init()
        internal_pis = [TPI.PI1.knob_value, TPI.PI2.knob_value]
        external_pis = [TPI.PI3.knob_value]
        knobs = [k.knob_value for k in list(ToyKnobs)]
        reward_model = SingleTuning2ProportionMetricsReward([TPI.PI3.knob_value], external_pis, TPI.PI3.knob_value,
                                                            RewardType.REWARD_2A)
        enable_observation_normalizer = True
        self.environment = ToyEnvironment(internal_pis, external_pis, knobs, reward_model,
                                          enable_observation_normalizer=enable_observation_normalizer)

    def test_env(self):
        tf_agents.environments.validate_py_environment(self.environment, episodes=1)

    # def test_step(self):
    #     self.environment.step()
