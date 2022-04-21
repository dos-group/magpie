from unittest import TestCase

from magpie.config.config import WorkloadSettings
from magpie.utils import magpie_logging
from magpie.utils.dd_utils import DDUtils


class TestDDUtils(TestCase):
    def setUp(self) -> None:
        magpie_logging.init()

    def test_start_workload(self):
        print(DDUtils(WorkloadSettings()).start_workload(count=200))
