from unittest import TestCase

from magpie.types.workload import Workload


class TestWorkload(TestCase):

    def test_represetnation(self):
        print(Workload.SEQUENTIAL_10M_WRITE_20_JOBS.__str__())

    def test_to_fio_params(self):
        self.fail()
