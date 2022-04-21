from unittest import TestCase

from magpie.config.config import InfluxdbSettings, LustrePIsSettings
from magpie.environment.collector import InfluxDBCollector
from magpie.environment.toy.toy_dfs_collector import ToyDFSCollector
from magpie.utils import magpie_logging


class TestInfluxDBCollector(TestCase):
    def setUp(self) -> None:
        magpie_logging.init()
        lustre_pis_settings = LustrePIsSettings()
        pis = lustre_pis_settings.file_system + lustre_pis_settings.cpu + lustre_pis_settings.ram
        self.db_collector = InfluxDBCollector(InfluxdbSettings(), pis)

    def test__get_pis(self):
        internal, external = self.db_collector.get_pis(3)
        self.assertIsNotNone(internal)
        self.assertIsNotNone(external)

    def test_get_throughput(self):
        pis = self.db_collector.get_pis(3)
        throughput = self.db_collector.get_throughput(pis)
        print(throughput)
        self.assertIsNotNone(throughput)

    def test__get_all_dataframe(self):
        dataframe = self.db_collector._get_all_dataframe(2)


class TestToyDFSCollector(TestCase):
    def setUp(self) -> None:
        magpie_logging.init()
        self.toy_collector = ToyDFSCollector([1, 2])

    def test_get_pis(self):
        self.toy_collector.get_pis(3)