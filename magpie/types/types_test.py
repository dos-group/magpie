from unittest import TestCase

from magpie.environment.toy_env.toy_knobs import ToyKnobs

from magpie.types.dfs_configuration import TuneParameter, ScopedTuneParameters
from magpie.types.rl_model import RLModel


class TestType(TestCase):

    def test_dfs_type(self):
        ppo = RLModel.PPO
        print(ppo)

    def test_str(self):
        parameter = TuneParameter(ToyKnobs.KNOB1.knob_value, 2)
        # print([parameter])
        print(ScopedTuneParameters("hi", [parameter]))
