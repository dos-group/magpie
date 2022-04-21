import datetime
import logging
import time
from typing import List

import numpy as np
import pandas as pd

from magpie.config.config import InfluxdbSettings, LustrePIsSettings
from magpie.environment.lustre.lustre_performance_indicators import LustrePerformanceIndicators as LPI
from magpie.types.external_metrics import ExternalMetrics, LustreExternalMetrics
from magpie.types.performance_indicator import FloatPerformanceIndicator
from magpie.utils.influxdb_api import InfluxDBAPI


class Collector:
    """
    performance indicator collector
    """
    logger = logging.Logger(__name__)

    def get_pis(self, observation_time: int = None, start_time:float = None, end_time:float = None,wait_for_observation=True) -> (np.array, ExternalMetrics):
        """
        get performance indicators
        :param current_ts: current timestamp
        :param observation_time: observation time in second
        :param wait_for_observation: wait for observation_time to collect metrics
        :return:
        """
        if observation_time is not None and (start_time is not None or end_time is not None):
            raise AttributeError(f"It's illegal to set observation time and start time or end time at the same time.")
        if observation_time is not None and wait_for_observation:
            self.logger.debug(f"pis observation time {observation_time}")
            time.sleep(observation_time)
        pis = self._get_pis(observation_time, start_time, end_time)
        return pis

    def _get_pis(self, observation_time: int = None, start_time: float = None, end_time: float = None) -> (
            np.array, ExternalMetrics):
        raise NotImplementedError


class InfluxDBCollector(Collector):
    logger = logging.Logger(__name__)

    def __init__(self, influxdb_setting: InfluxdbSettings, internal_pis: List[FloatPerformanceIndicator]):
        self.internal_pis = internal_pis
        self.influxdb_api = InfluxDBAPI(influxdb_setting)
        self.internal_columns = [pi_format.alias or pi_format.name for pi_format in self.internal_pis]
        with open(LustrePIsSettings().query_file, "r") as f:
            self.pis_flux_query = f.read()

    def get_throughput(self, metrics_df: pd.DataFrame) -> np.float:
        write_rates = metrics_df[LPI.WRITE_BYTES_RATE.get_alias_or_name()].item() or 0
        read_rates = metrics_df[LPI.READ_BYTES_RATE.get_alias_or_name()].item() or 0
        return read_rates + write_rates

    def get_iops(self, metrics_df: pd.DataFrame):
        write_iops_rates = metrics_df[LPI.WRITE_IOPS_RATE.get_alias_or_name()].item()
        read_iops_rates = metrics_df[LPI.READ_IOPS_RATE.get_alias_or_name()].item()
        return read_iops_rates + write_iops_rates

    def _get_pis(self, observation_time: int = None, start_time: float = None, end_time: float = None) -> (
            np.array, LustreExternalMetrics):
        if observation_time is not None:
            start_time = datetime.timedelta(seconds=-1 * observation_time)
            end_time = datetime.timedelta(milliseconds=-1)
        else:
            now = time.time()
            end_delta = int(end_time - now)
            start_delta = int(start_time - now)
            start_time = datetime.timedelta(seconds=start_delta)
            end_time = datetime.timedelta(seconds=end_delta)
        dataframe = self.influxdb_api.query_data_frame(self.pis_flux_query, start_time, end_time)
        internal_metrics = dataframe[self.internal_columns].to_numpy(dtype=np.float32).flatten()
        external_metrics = LustreExternalMetrics(self.get_throughput(dataframe), self.get_iops(dataframe))
        return internal_metrics, external_metrics
