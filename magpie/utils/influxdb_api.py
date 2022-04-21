import datetime
import logging
import socket
from typing import Union, Dict

from devtools import pformat
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS

from magpie.config.config import InfluxdbSettings


class InfluxDBAPI:
    def __init__(self, influxdb_setting: InfluxdbSettings):
        self.logger = logging.getLogger(__name__)
        self.magpie_bucket = influxdb_setting.magpie_bucket
        self.influx_client = InfluxDBClient(influxdb_setting.url, influxdb_setting.token, org=influxdb_setting.org)
        self.async_write_api = self.influx_client.write_api(write_options=ASYNCHRONOUS)
        self.executor_hostname = socket.gethostname()

    def __del__(self):
        self.influx_client.close()

    def query_data_frame(self, query, start_time: Union[datetime.timedelta], end_time: Union[datetime.timedelta]):
        query_api = self.influx_client.query_api()
        params = {"_start": start_time,
                  "_end": end_time
                  }
        data_frame = query_api.query_data_frame(query, params=params)
        self.logger.debug(f"query result: {pformat(data_frame)}")
        return data_frame

    def async_write(self, data: Dict):
        record = {"measurement": "action", "tags": {"controller": self.executor_hostname},
                  "fields": data, "time": datetime.datetime.utcnow()}
        self.async_write_api.write(self.magpie_bucket, record=record)
