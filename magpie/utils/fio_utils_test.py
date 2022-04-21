from unittest import TestCase

from magpie.config.config import FioSettings
from magpie.types.workload import Workload
from magpie.utils.fio_utils import FioUtils
from magpie.utils.magpie_logging import init

init()

class Test(TestCase):
    def test_section(self):
        settings = FioSettings()
        settings.workload=Workload.RANDOM_4K_90PCT_READ
        utils = FioUtils(settings)
        utils.start_workload()

    def test_generate(self):
        workload = Workload.SEQUENTIAL_10M_WRITE
        settings = FioSettings()
        utils = FioUtils(settings)
        utils.generate_fio_conf(workload)


    def test(self):
        print(Workload.SEQUENTIAL_10M_WRITE.io_type)
        FioSettings(workload=Workload.SEQUENTIAL_10M_WRITE.value)