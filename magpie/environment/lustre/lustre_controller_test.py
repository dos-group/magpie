from unittest import TestCase

from magpie.config.config import LustreSettings, LustreKnobsSettings
from magpie.environment.lustre.lustre_controller import LustreController
from magpie.environment.lustre.lustre_knobs import LustreKnobs
from magpie.types.dfs_configuration import TuneParameter
from magpie.utils import magpie_logging


class TestLustreController(TestCase):
    def setUp(self) -> None:
        magpie_logging.init()

    def test_reset_params(self):
        all_knobs = LustreKnobsSettings().get_all_knobs()
        LustreController(LustreSettings()).reset_params(all_knobs)

    def test_set_param(self):
        params = [
            # TuneParameter(LustreKnobs.MAX_DIRTY_MB.knob, 516),
            TuneParameter(LustreKnobs.MAX_RPCS_IN_FLIGHT.knob, 16),
            # TuneParameter(LustreKnobs.MAX_PAGES_PER_RPC.knob, 3961),
            #
            # TuneParameter(LustreKnobs.MAX_CACHED_MB.knob, 12288),
            # TuneParameter(LustreKnobs.STRIPE_SIZE.knob, 946),
            # TuneParameter(LustreKnobs.STRIPE_COUNT.knob, 10),
                  ]
        LustreController(LustreSettings()).set_params(params)

    def test_stripe_param_set(self):
        params = [
            TuneParameter(LustreKnobs.STRIPE_SIZE.knob, 2),
            TuneParameter(LustreKnobs.STRIPE_COUNT.knob, 2),
        ]
        LustreController(LustreSettings()).set_params(params)