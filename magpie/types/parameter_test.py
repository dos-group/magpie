from unittest import TestCase

from devtools import pformat
from magpie.environment.lustre_knobs import LustreKnobs
from magpie.types.parameter import LustreTuneParameter


class TestLustreTuneParameter(TestCase):
    def test_lustre_parameter(self):
        parameter = LustreTuneParameter(LustreKnobs.MAX_RPCS_IN_FLIGHT.knob_value, 20)
        print(pformat(parameter))
