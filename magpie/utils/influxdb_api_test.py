import time
from unittest import TestCase

from magpie.config.config import InfluxdbSettings
from magpie.utils.influxdb_api import InfluxDBAPI


class TestInfluxDBAPI(TestCase):

    def setUp(self) -> None:
        self.dbapi = InfluxDBAPI(InfluxdbSettings())

    def test_async_write_data(self):
        data = {"p1":12, "p2":13}
        self.dbapi.async_write(data)
        time.sleep(1)
        data = {"p1":14, "p2":15}
        self.dbapi.async_write(data)
