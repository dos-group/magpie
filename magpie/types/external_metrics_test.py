from unittest import TestCase

from magpie.types.external_metrics import ToyExternalMetrics


class TestToyExternalMetrics(TestCase):
    def test_lt(self):
        metrics = ToyExternalMetrics(20)
        metrics2 = ToyExternalMetrics(30)
        self.assertLess(metrics, metrics2)
