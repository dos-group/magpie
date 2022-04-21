from unittest import TestCase

from devtools import pformat

from magpie.environment.lustre.lustre_performance_indicators import LustrePerformanceIndicators as LPI
from magpie.environment.reward import SingleTuning2ProportionMetricsReward, SingleTuning3ProportionMetricsReward, \
    SingleTuning2ProportionMetricsRewardWithMovingAvg
from magpie.types.external_metrics import LustreExternalMetrics
from magpie.types.reward_type import RewardInput
from magpie.types.reward_type import RewardType
from magpie.utils import magpie_logging

magpie_logging.init()


class TestSingleTuning2ProportionMetricsReward(TestCase):

    def setUp(self) -> None:
        self.init_metrics = LustreExternalMetrics(2000, 1000)
        self.previous_metrics = LustreExternalMetrics(3020, 1200)
        self.best_metrics = LustreExternalMetrics(3031, 1200)
        self.current_metrics = LustreExternalMetrics(3000, 1100)

    def test_calculate(self):
        # reward 2a
        self.verify_reward2x(RewardType.REWARD_2A, self.previous_metrics)
        # reward 2b
        self.verify_reward2x(RewardType.REWARD_2B, self.init_metrics)
        # reward 2c
        self.verify_reward2x(RewardType.REWARD_2C, self.best_metrics)

    def verify_reward2x(self, reward_type: RewardType, last_metrics):
        reward_model = SingleTuning2ProportionMetricsReward(LustreExternalMetrics.get_throughput, reward_type)
        reward_input = RewardInput(self.init_metrics, self.best_metrics, self.previous_metrics, self.current_metrics)
        reward = reward_model.calculate(reward_input)
        expected_reward = (self.current_metrics.throughput - last_metrics.throughput) / last_metrics.throughput
        self.assertEqual(reward, expected_reward)


class TestSingleTuning2ProportionMetricsRewardWithMovingAvg(TestCase):
    def setUp(self) -> None:
        self.metric0 = LustreExternalMetrics(2000, 1000)
        self.metric1 = LustreExternalMetrics(3020, 1200)
        self.metric2 = LustreExternalMetrics(3031, 1200)
        self.metric3 = LustreExternalMetrics(3500, 1100)

    def test_reward_1a(self):
        reward_input = RewardInput(self.metric0, self.metric0, self.metric0, self.metric1)
        RewardType.REWARD_1A.func(reward_input, lambda  x: print(x))
        RewardType.REWARD_2A.func(reward_input, lambda  x,y: print(x,y))

    def test_calculation(self):
        reward_model = SingleTuning2ProportionMetricsRewardWithMovingAvg(LustreExternalMetrics.get_throughput,
                                                                         buffer_size=2)
        reward_input = RewardInput(self.metric0, self.metric0, self.metric0, self.metric0)
        reward = reward_model.calculate(reward_input)
        self.assertEqual(reward, 0)
        reward_input = RewardInput(self.metric0, self.metric0, self.metric0, self.metric1)
        reward = reward_model.calculate(reward_input)
        reward_input = RewardInput(self.metric0, self.metric0, self.metric0, self.metric2)
        reward = reward_model.calculate(reward_input)
        prev_avg = (self.metric0.throughput + self.metric1.throughput) / 2
        expected = (self.metric2.throughput - prev_avg) / prev_avg - 0.05
        self.assertEqual(reward, expected)
        reward_input = RewardInput(self.metric0, self.metric0, self.metric0, self.metric3)
        prev_avg = (self.metric1.throughput + self.metric2.throughput) / 2
        expected = (self.metric3.throughput - prev_avg) / prev_avg - 0.05
        reward = reward_model.calculate(reward_input)
        self.assertEqual(reward, expected)


class TestSingleTuning3ProportionMetricsReward(TestCase):
    def setUp(self) -> None:
        self.init_metrics = LustreExternalMetrics(2000, 1000)
        self.previous_metrics = LustreExternalMetrics(3020, 1200)
        self.best_metrics = LustreExternalMetrics(3031, 1200)
        self.current_metrics = LustreExternalMetrics(3000, 1100)

    def test_calculation(self):
        with self.assertRaises(ValueError):
            self.verify_reward3x(RewardType.REWARD_3A, 0)
        expected_reward = self.proportion3(self.init_metrics, self.best_metrics,
                                           self.current_metrics)
        self.verify_reward3x(RewardType.REWARD_3B, expected_reward)
        expected_reward = self.proportion3(self.best_metrics, self.previous_metrics,
                                           self.current_metrics)
        self.verify_reward3x(RewardType.REWARD_3C, expected_reward)

    def proportion3(self, base_metrics, pivot_metrics, current_metrics):
        def calculate_proportion(current_metrics, base_metrics):
            return (current_metrics.throughput - base_metrics.throughput) / base_metrics.throughput

        delta_t = calculate_proportion(current_metrics, pivot_metrics)
        delta_0 = calculate_proportion(current_metrics, base_metrics)
        return SingleTuning3ProportionMetricsReward._calculate_reward(delta_0, delta_t)

    def verify_reward3x(self, reward_type: RewardType, expected_reward):
        external_pis = [LPI.READ_BYTES_RATE.value, LPI.WRITE_BYTES_RATE.value]
        reward_model = SingleTuning3ProportionMetricsReward(LustreExternalMetrics.get_throughput, reward_type)
        reward_input = RewardInput(self.init_metrics, self.best_metrics, self.previous_metrics, self.current_metrics)
        reward = reward_model.calculate(reward_input)
        print(f"{pformat(reward_type)}, reward={reward}")
        self.assertEqual(reward, expected_reward)
