import logging
import time
from typing import List, Union, Callable, Any, Optional

import tensorflow as tf

from magpie.config.config import FioSettings, InfluxdbSettings, WorkloadSettings
from magpie.environment.collector import Collector
from magpie.environment.controller import DistributedDFSController, CentralDFSController
from magpie.environment.dfs_environment import DFSEnvironment
from magpie.environment.lustre.lustre_knobs import LustreKnobs
from magpie.environment.reward import Reward
from magpie.types.dfs_configuration import DFSConfiguration
from magpie.types.external_metrics import ExternalMetrics, LustreExternalMetrics
from magpie.types.knob import Knob
from magpie.types.performance_indicator import FloatPerformanceIndicator
from magpie.utils.dd_utils import DDUtils
from magpie.utils.fio_utils import FioUtils
from magpie.utils.influxdb_api import InfluxDBAPI


class LustreEnvironment(DFSEnvironment):
    """
    Lustre Environment
    """
    CORE_INFO_LOGGER = logging.getLogger("core_info")

    def __init__(self, internal_pis: List[FloatPerformanceIndicator],
                 knobs: List[Knob], controller: Union[DistributedDFSController, CentralDFSController],
                 collector: Collector, reward: Reward, observation_time,
                 fio_settings: Optional[FioSettings],
                 influxdb_settings: InfluxdbSettings,
                 delay_after_fio_startup=15,
                 step_observers: List[Callable[[DFSConfiguration, Any, ExternalMetrics, float], None]] = [],
                 debug=False,
                 dd_workload=False,
                 **kwargs):
        """

        :param internal_pis:
        :param knobs:
        :param controller:
        :param collector:
        :param reward:
        :param observation_time:
        :param fio_settings:
        :param influxdb_settings:
        :param delay_after_fio_startup:
        :param step_observers:
        :param debug:
        :param kwargs:
        """
        self.influxdb_api = InfluxDBAPI(influxdb_settings)
        step_observers.append(self.action_observer)
        super().__init__(internal_pis, LustreExternalMetrics, knobs, controller, collector, reward, observation_time,
                         step_observers=step_observers, debug=debug, dd_workload=dd_workload, **kwargs)
        if fio_settings is not None:
            if dd_workload is False:
                self.fio_util = FioUtils(fio_settings)
            else:
                raise ValueError("Parameter error! dd workload and fio can't be together.")
        # delay time before fetching performance indicators from DFS
        if dd_workload:
            self.dd_util = DDUtils(WorkloadSettings())
        self.delay_after_fio_startup = delay_after_fio_startup
        if self.debug:
            self.observation_time = 5
            self.delay_after_fio_startup = 0

    def action_observer(self, new_parameters: DFSConfiguration, current_state,
                        current_external_metrics: ExternalMetrics,
                        reward):
        result = {}
        for scope in new_parameters.configuration:
            for param in scope.parameters:
                result[param.name.name] = param.value
        step_performance = {"step": tf.compat.v1.train.get_or_create_global_step().numpy(), "config": result,
                            "performance": current_external_metrics}
        self.CORE_INFO_LOGGER.info(step_performance)
        self.influxdb_api.async_write(result)

    def _initialization(self):
        """
        initialize Lustre and start Fio workloads
        :return:
        """
        if not self.debug:
            # reset all lustre knobs to default
            all_knobs = [knob_enum.knob for knob_enum in list(LustreKnobs)]
            self.controller.reset_params(all_knobs)
            if hasattr(self, "fio_util"):
                self.logger.info("Start Fio workload.")
                self.fio_util.start_workload()
                time.sleep(self.delay_after_fio_startup)
            elif hasattr(self, "dd_util"):
                self.logger.info("Start DD workload.")
                start_time = time.time()
                self.dd_util.start_workload()
                return start_time
            else:
                self.logger.info("Use manual workload.")
