from unittest import TestCase

import numpy

from magpie.types.knob import IntKnob


class TestKnob(TestCase):

    def test_check_numerical_range_validity(self):
        IntKnob(name="test", default=1, min=1, max=10)
        with self.assertRaises(ValueError):
            IntKnob(name="test", default=1, min=1, max=-1)
        with self.assertRaises(ValueError):
            IntKnob(name="test", default=11, min=1, max=10)

    def test_knob_type(self):
        knob = IntKnob(name="test", default=1, min=1, max=10)
        self.assertEqual(knob.type, numpy.int, f"knob type: {knob.type}")
