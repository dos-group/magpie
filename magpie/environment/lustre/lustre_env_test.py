import tf_agents

from magpie.environment.reward import SingleTuning2ProportionMetricsReward
from magpie.types.external_metrics import LustreExternalMetrics
from magpie.types.reward_type import RewardType
from magpie.utils import magpie_logging

magpie_logging.init()
from unittest import TestCase

from tf_agents.trajectories import TimeStep

from magpie.config.config import LustreSettings, InfluxdbSettings
from magpie.environment.collector import InfluxDBCollector
from magpie.environment.lustre.lustre_controller import LustreController
from magpie.environment.lustre.lustre_env import LustreEnvironment
from magpie.environment.lustre.lustre_knobs import LustreKnobs
from magpie.environment.lustre.lustre_performance_indicators import LustrePerformanceIndicators


class TestLustreEnvironment(TestCase):
    def setUp(self) -> None:
        lustre_settings = LustreSettings()
        influxdb_settings = InfluxdbSettings()
        pis = [LustrePerformanceIndicators.READ_BYTES_RATE.value, LustrePerformanceIndicators.WRITE_BYTES_RATE.value]
        knobs = [LustreKnobs.STRIPE_COUNT.knob, LustreKnobs.STRIPE_SIZE.knob]
        controller = LustreController(lustre_settings)
        collector = InfluxDBCollector(influxdb_settings, pis)
        reward = SingleTuning2ProportionMetricsReward(LustreExternalMetrics.get_throughput, RewardType.REWARD_2B)
        settings = None
        # settings = FioSettings()
        # settings.workload=Workload.RANDOM_4K_90PCT_READ
        self.lustre_environment = LustreEnvironment(pis, knobs, controller, collector, reward,
                                                    fio_settings=settings,
                                                    influxdb_settings=influxdb_settings,
                                                    observation_time=10,
                                                    dd_workload=True,
                                                    debug=False)

    def test_env(self):
        tf_agents.environments.validate_py_environment(self.lustre_environment, episodes=1)

    def test__reset(self):
        self.lustre_environment.reset()

    def test_get_state(self):
        state = self.lustre_environment.get_state()
        observation_spec = self.lustre_environment.observation_spec()
        self.assertTrue(observation_spec.check_array(state))

    def test__reward(self):
        ts: TimeStep = self.lustre_environment.reset()
        current_state = self.lustre_environment.get_state()
        self.assertIsNotNone(current_state)
        reward = self.lustre_environment._reward(current_state)
        self.assertGreaterEqual(reward, 0)

    def test__initialization(self):
        self.lustre_environment._initialization()

    def test_reset(self):
        self.lustre_environment.reset()