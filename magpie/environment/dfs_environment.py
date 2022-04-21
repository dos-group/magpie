import heapq
import logging
import time
from collections import defaultdict
from typing import Any, List, Union, Type, Callable

import numpy as np
import tensorflow as tf
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
from tf_agents.typing import types

from magpie.config.config import WorkloadSettings
from magpie.environment.collector import Collector
from magpie.environment.controller import DistributedDFSController, CentralDFSController
from magpie.environment.reward import Reward
from magpie.types.dfs_configuration import TuneParameter, ScopedTuneParameters, ConfigurationScorePair, DFSConfiguration
from magpie.types.external_metrics import ExternalMetrics
from magpie.types.knob import Knob
from magpie.types.performance_indicator import FloatPerformanceIndicator
from magpie.types.reward_type import RewardInput
from magpie.utils.dd_utils import DDUtils


class Normalizer:
    def __init__(self, pis: List[FloatPerformanceIndicator]):
        max_arr = np.array([pi.max for pi in pis], dtype=np.float32)
        self.min_arr = np.array([pi.min for pi in pis], dtype=np.float32)
        self.range = max_arr - self.min_arr

    def normalize(self, value):
        return (value - self.min_arr) / self.range


class DFSEnvironment(py_environment.PyEnvironment):
    """
    DFS Environment
    """
    logger = logging.getLogger(__name__)

    def __init__(self, internal_pis: List[FloatPerformanceIndicator],
                 external_metrics_cls: Type[ExternalMetrics], knobs: List[Knob],
                 controller: Union[DistributedDFSController, CentralDFSController], collector: Collector,
                 reward: Reward,
                 observation_time: int,
                 debug=False,
                 enable_observation_normalizer=True,
                 step_observers: Callable[[DFSConfiguration, Any, ExternalMetrics, float], None] = None,
                 summary_step_observer: bool = True,
                 dd_workload: bool = False,
                 **kwargs):
        super().__init__()
        self.dd_workload = dd_workload
        if self.dd_workload:
            self.dd_util = DDUtils(WorkloadSettings())
        self.external_metrics_cls = external_metrics_cls
        self.knobs = knobs
        self.enable_observation_normalizer = enable_observation_normalizer
        self._step_observers = step_observers or []
        if summary_step_observer:
            self._step_observers += [self.summary_step_observer]
        self._action_spec = array_spec.BoundedArraySpec(shape=(len(knobs),), dtype=np.float32, minimum=0, maximum=1,
                                                        name="action")
        if enable_observation_normalizer:
            minimum = 0
            maximum = 1.0
        else:
            minimum = [pi.min for pi in internal_pis]
            maximum = [pi.max for pi in internal_pis]
        self._observation_spec = array_spec.BoundedArraySpec(shape=(len(internal_pis),), dtype=np.float32,
                                                             minimum=minimum,
                                                             maximum=maximum, name='observation')

        self.discount_factor = 1.0
        self.controller = controller
        self.collector = collector
        # delay time before fetching performance indicators from DFS
        self.reward_model = reward
        self.debug = debug
        if self.debug:
            self.logger.warning("Execute DFS environment in debug mode!")
        self.observation_time = observation_time
        self.delay_after_initialization = 10 if not self.dd_workload else 0
        self.observation_normalizer = Normalizer(internal_pis) if enable_observation_normalizer else None
        self.best_metrics: ExternalMetrics = None

    def set_state(self, state: Any) -> None:
        pass

    def observation_spec(self) -> types.NestedArraySpec:
        return self._observation_spec

    def action_spec(self) -> types.NestedArraySpec:
        return self._action_spec

    def get_metrics(self, observation_time=None, start_time=None, end_time=None) -> (np.array, ExternalMetrics):
        if self.dd_workload:
            internal_metrics, external_metrics = self.collector.get_pis(None, start_time, end_time)
        else:
            internal_metrics, external_metrics = self.collector.get_pis(observation_time or self.observation_time)
        if self.enable_observation_normalizer:
            normalized_internal_metrics = self.observation_normalizer.normalize(internal_metrics)
            self.logger.debug(
                f"internal metrics: {internal_metrics}, after normalization: {normalized_internal_metrics}")
            return normalized_internal_metrics, external_metrics
        return internal_metrics, external_metrics

    def _initialization(self):
        raise NotImplementedError

    def _reset(self) -> ts.TimeStep:
        # initialization
        self.logger.info("Start to reset environment.")
        initialization = self._initialization()
        if not self.debug and not self.dd_workload:
            self.logger.info(f"Sleep {self.delay_after_initialization} seconds after initialization.")
            time.sleep(self.delay_after_initialization)
        if self.dd_workload:
            if self.dd_util.type == "fio":
                start_time = initialization + 32
                end_time = time.time() - 1
                state, self.initial_metrics = self.get_metrics(None, start_time, end_time)
            else:
                start_time = initialization + 32
                end_time = time.time() - 1
                state, self.initial_metrics = self.get_metrics(None, start_time, end_time)
        else:
            state, self.initial_metrics = self.get_metrics(self.observation_time * 3)
        self.logger.info(f"initial metrics: {self.initial_metrics}")
        self.previous_metrics = self.initial_metrics
        self.best_metrics = self.previous_metrics
        self.good_configurations = []
        self.best_configuration_size = 5
        self.logger.info("Finish to reset environment.")
        return ts.restart(np.array(state, dtype=np.float32))

    @staticmethod
    def summary_step_observer(new_parameters: DFSConfiguration, current_state,
                              current_external_metrics: ExternalMetrics,
                              reward):
        log_str = ""
        for name, value in current_external_metrics.get_all_metrics().items():
            log_str += f" {name} metrics={value}"
            tf.summary.scalar(f"metric_{name}", value)
            tf.summary.scalar('training/reward', reward)
        DFSEnvironment.logger.info(log_str)

    def step_observe(self, new_parameters: DFSConfiguration, current_state,
                     current_external_metrics: ExternalMetrics,
                     reward):
        """
        observe each step
        :param new_parameters:
        :param current_state:
        :param current_external_metrics:
        :param reward:
        :return:
        """
        for fn in self._step_observers:
            fn(new_parameters, current_state, current_external_metrics, reward)

    def get_reward(self, current_metrics: ExternalMetrics) -> float:
        reward_input = RewardInput(self.initial_metrics, self.best_metrics, self.previous_metrics, current_metrics)
        return self.reward_model.calculate(reward_input)

    def generate_knobs(self, action: np.array) -> DFSConfiguration:
        """
        generate knobs for given actions
        :param knobs:
        :param action:
        :return: {knob_scope, [Knob, Knob_value]}
        """
        new_config = defaultdict(list)
        for knob, action_value in zip(self.knobs, action):
            assert 0 <= action_value <= 1, f"invalid action {action_value}, action value needs to be between 0 and 1"
            if knob.type is np.int or knob.type is np.float:
                new_value = knob.min + (knob.max - knob.min) * action_value
                new_value = int(new_value)
            else:
                raise NotImplementedError(f"knob type {knob.type} is not implemented.")
            tune_parameter = TuneParameter(knob, new_value)
            new_config[knob.scope].append(tune_parameter)
        result = DFSConfiguration(
            [ScopedTuneParameters(scope=scope, parameters=params) for scope, params in new_config.items()])
        return result

    def update_best_configuration(self, dfs_configuration: DFSConfiguration,
                                  new_metric: ExternalMetrics) -> bool:
        """
        compare new metrics, if it's better, set it to best metrics
        :param dfs_configuration:
        :param new_metric:
        :return:
        """
        new_is_better = self.best_metrics < new_metric
        if new_is_better:
            self.best_metrics = new_metric
        if len(self.good_configurations) < self.best_configuration_size:
            heapq.heappush(self.good_configurations,
                           ConfigurationScorePair(dfs_configuration, new_metric))
        else:
            heapq.heappushpop(self.good_configurations,
                              ConfigurationScorePair(dfs_configuration, new_metric))
        # self.logger.debug(f"best configuration queue: {self.good_configurations}")
        return new_is_better

    def get_info(self) -> ExternalMetrics:
        return self.previous_metrics

    def _step(self, action: types.NestedArray) -> ts.TimeStep:
        # self.logger.debug(f"agent's new action = {pformat(action)}")
        new_configuration = self.generate_knobs(action)
        self.apply_configuration(new_configuration)
        if self.dd_workload:
            start_time, end_time = self._start_offline_workload(self.dd_util)
            current_state, current_external_metrics = self.get_metrics(None, start_time, end_time)
        else:
            current_state, current_external_metrics = self.get_metrics()
        reward = self.get_reward(current_external_metrics)
        self.step_observe(new_configuration, current_state, current_external_metrics, reward)
        self.update_best_configuration(new_configuration, current_external_metrics)
        self.previous_metrics = current_external_metrics
        return ts.transition(current_state, reward=reward, discount=self.discount_factor)

    def apply_configuration(self, new_configuration: DFSConfiguration):
        if self.debug:
            self.logger.warning(f"Doesn't apply new configuration in debug mode!")
            return
        for scope_parameters in new_configuration:
            self.controller.set_params(scope_parameters)
        self.logger.info(f"apply new configuration, {new_configuration.__repr__()}")

    @staticmethod
    def _start_offline_workload(dd_util, clean_wait_sec: int = 20, start_ramp_sec: int = 12, end_ramp_sec: int = 11, eval=False):
        dd_util.clean()
        DFSEnvironment.logger.info(f"sleep {clean_wait_sec} seconds")
        time.sleep(clean_wait_sec)
        DFSEnvironment.logger.info(f"start workload")
        start_time = time.time() + start_ramp_sec
        dd_util.start_workload(eval=eval)
        end_time = time.time() - end_ramp_sec
        return start_time, end_time

    def evaluate_configuration(self, configuration: DFSConfiguration,
                               observation_time: int = None) -> ConfigurationScorePair:
        """
        evaluate a configuration
        :param configuration:
        :param observation_time:
        :return:
        """
        self.apply_configuration(configuration)
        if self.dd_workload:
            if observation_time is not None:
                raise AttributeError("observation_time needs to be None!")
            start_time, end_time = self._start_offline_workload(self.dd_util, eval=True)
            _, external_metrics = self.collector.get_pis(None, start_time, end_time)
        else:
            _, external_metrics = self.collector.get_pis(observation_time)
        return ConfigurationScorePair(configuration, external_metrics)
