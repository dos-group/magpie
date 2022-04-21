import logging
import math
from typing import Optional, Callable

import numpy as np
import tensorflow as tf
from devtools import pformat
from tf_agents.metrics.py_metrics import NumpyDeque

from magpie.types.external_metrics import ExternalMetrics
from magpie.types.reward_type import RewardType, RewardInput


class Reward:

    def __init__(self, get_metric_a: Callable[[ExternalMetrics], float],
                 reward_type: RewardType,
                 get_metric_b: Optional[Callable[[ExternalMetrics], float]] = None):
        self.logger = logging.getLogger(__name__)
        self.reward_type = reward_type
        self.get_metric_a = get_metric_a
        if get_metric_b is not None:
            self.get_metric_b = get_metric_b

    def calculate(self, reward_input: RewardInput) -> float:
        return self.reward_type.func(reward_input, self._calculate)

    def _calculate(self, *args, **kwargs) -> float:
        raise NotImplementedError


class DoubleTuning2ProportionMetricsReward(Reward):
    """
    Double Tuning goal with 2 metrics calculated as proportional reward
    """

    def get_scalarization_value(self, metrics: ExternalMetrics):
        value_a = self.get_metric_a(metrics)
        value_b = self.get_metric_b(metrics)
        value = value_a / 10000000 + value_b / 10
        return value

    def _calculate(self, past_metrics: ExternalMetrics, current_metrics: ExternalMetrics) -> float:
        """
        :param past_metrics: past metrics could be previous, initial or best metrics
        :param current_metrics:
        :return:
        """
        self.logger.debug(f"past {past_metrics}, current {current_metrics}")
        prev_value = self.get_scalarization_value(past_metrics)
        if prev_value == 0:
            raise ValueError(
                f"Initial or previous metric is 0! previous_metrics={pformat(past_metrics)}")
        current_value = self.get_scalarization_value(current_metrics)
        delta = (current_value - prev_value) / prev_value
        return delta


class SingleTuning2ProportionMetricsReward(Reward):
    """
    Single Tuning goal with 2 metrics calculated as proportional reward
    """

    def __init__(self, get_metric_a: Callable[[ExternalMetrics], float], reward_type: RewardType):
        super().__init__(get_metric_a, reward_type)

    def _calculate(self, past_metrics: ExternalMetrics, current_metrics: ExternalMetrics) -> float:
        """
        :param past_metrics: past metrics could be previous, initial or best metrics
        :param current_metrics:
        :return:
        """
        self.logger.debug(f"past {past_metrics}, current {current_metrics}")
        prev_value = self.get_metric_a(past_metrics)
        if prev_value == 0 or prev_value == 0:
            raise ValueError(
                f"Initial or previous metric is 0! previous_metrics={pformat(past_metrics)}")
        current_value = self.get_metric_a(current_metrics)
        delta = (current_value - prev_value) / prev_value
        return delta


class SingleTuning2ProportionMetricsRewardWithMovingAvg(Reward):
    """
    Single Tuning goal with 2 metrics calculated as proportional reward with moving average
    """

    def __init__(self, get_metric_a: Callable[[ExternalMetrics], float], tolerance_ratio=0.05,
                 buffer_size=10):
        """

        :param get_metric_a:
        :param reward_type:
        :param tolerance_ratio: the ratio of performance variance which is ignored, e.g., if performance is increased 5%
        and the tolerance_ratio is set to 6%, it will be regarded as no changes in performance, thus no reward.
        :param buffer_size:
        """
        super().__init__(get_metric_a, RewardType.REWARD_1A)
        self._tolerance_ratio = tolerance_ratio
        self._buffer = NumpyDeque(maxlen=buffer_size, dtype=np.float32)

    def _calculate(self, current_metrics: ExternalMetrics) -> float:
        current_value = self.get_metric_a(current_metrics)
        if self._buffer.__len__() == 0:
            self._buffer.extend([current_value])
            return 0
        moving_avg = self._buffer.mean()
        tf.summary.scalar("moving average", moving_avg)
        self._buffer.extend([current_value])
        increase_ratio = (current_value - moving_avg) / moving_avg
        if -1 * self._tolerance_ratio <= increase_ratio <= self._tolerance_ratio:
            return 0
        else:
            return increase_ratio + self._tolerance_ratio if increase_ratio < 0 else increase_ratio - self._tolerance_ratio


class SingleTuning3ProportionMetricsReward(Reward):
    """
    Single Tuning goal with 3 metrics calculated as proportional reward
    """

    def __init__(self, get_metric_a: Callable[[ExternalMetrics], float], reward_type: RewardType):
        self.logger = logging.getLogger(__name__)
        if reward_type.num_args_return != 3 or reward_type is RewardType.REWARD_3A:
            self.logger.error(f"Reward type is error,current: {reward_type}")
            raise ValueError
        super().__init__(get_metric_a, reward_type)

    @staticmethod
    def _calculate_reward(delta_0, delta_t):

        if delta_0 > 0:
            _reward = ((1 + delta_0) ** 2 - 1) * math.fabs(1 + delta_t)
        else:
            _reward = - ((1 - delta_0) ** 2 - 1) * math.fabs(1 - delta_t)

        if _reward > 0 and delta_t < 0:
            _reward = 0
        return _reward

    def _calculate(self, metrics_1: ExternalMetrics, metrics_2: ExternalMetrics,
                   current_metrics: ExternalMetrics) -> float:
        """
        :param metrics_1: past metrics could be previous, initial
        :param metrics_2
        :param current_metrics:
        :return:
        """
        self.logger.debug(f"metrics_1 {metrics_1}, metrics_2 {metrics_2}, current {current_metrics}")
        if self.reward_type is RewardType.REWARD_3B:
            past_metrics = metrics_1
            best_metrics = metrics_2
        elif self.reward_type is RewardType.REWARD_3C:
            past_metrics = metrics_2
            best_metrics = metrics_1
        else:
            raise NotImplementedError
        past_metric_a = self.get_metric_a(past_metrics)
        best_metric_a = self.get_metric_a(best_metrics)
        if past_metric_a == 0 or best_metric_a == 0:
            raise ValueError(
                f"Initial or previous metric is 0! past_metrics={pformat(past_metrics)}, best_metrics={pformat(best_metrics)}")
        current_metric_a = self.get_metric_a(current_metrics)
        if self.reward_type is RewardType.REWARD_3B:
            delta_t_metric_a = (current_metric_a - best_metric_a) / best_metric_a
            delta_0_metric_a = (current_metric_a - past_metric_a) / past_metric_a
        elif self.reward_type is RewardType.REWARD_3C:
            delta_t_metric_a = (current_metric_a - past_metric_a) / past_metric_a
            delta_0_metric_a = (current_metric_a - best_metric_a) / best_metric_a
        metric_a_reward = self._calculate_reward(delta_0_metric_a, delta_t_metric_a)
        return metric_a_reward
