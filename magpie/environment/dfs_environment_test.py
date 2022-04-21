from unittest import TestCase

import numpy as np
from devtools import pformat

from magpie.environment.dfs_environment import Normalizer
from magpie.environment.lustre.lustre_performance_indicators import LustrePerformanceIndicators
from magpie.environment.toy.toy_knobs import ToyKnobs
from magpie.types.dfs_configuration import TuneParameter, ScopedTuneParameters, ConfigurationScorePair, DFSConfiguration
from magpie.types.external_metrics import ToyExternalMetrics


class TestConfigurationScorePair(TestCase):
    def test_print(self):
        tune_parameter = TuneParameter(ToyKnobs.KNOB1.value, 20)
        parameters = ScopedTuneParameters("hi", [tune_parameter])
        pair = ConfigurationScorePair(DFSConfiguration(configuration=[parameters]), ToyExternalMetrics(10))

        print(f"tune_parameter: {tune_parameter}, parameters: {parameters}, \npair: {pformat(pair)}")


class TestNormalizer(TestCase):
    def test_normalize(self):
        normalizer = Normalizer(
            [LustrePerformanceIndicators.READ_RPCS_IN_FLIGHT.value, LustrePerformanceIndicators.READ_IOPS_RATE.value])
        normalize = normalizer.normalize(np.array([12, 32]))
        expected = np.array([12 / 256 / 4, 0.032])
        self.assertTrue((expected == normalize).all())
