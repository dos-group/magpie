import copy
import logging

import numpy as np

from magpie.environment.collector import Collector
from magpie.types.external_metrics import ToyExternalMetrics


class ToyDFSCollector(Collector):
    logger = logging.getLogger(__name__)

    def __init__(self, toy_config):
        self.toy_config = toy_config

    def _get_pis(self, observation_time, start_time, end_time) -> (np.array, ToyExternalMetrics):
        self.logger.debug("small test in toy")
        toy_config = copy.deepcopy(self.toy_config)
        performance = 0.3 * toy_config[0] + 0.1 * toy_config[1]
        return np.array(toy_config, dtype=np.float32), ToyExternalMetrics(performance)
