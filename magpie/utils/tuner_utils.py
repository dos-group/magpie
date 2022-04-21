import logging
from typing import List

from devtools import pformat
from tf_agents.environments import TFPyEnvironment, ActionClipWrapper

from magpie.config.config import LustreSettings, LustrePIsSettings, LustreKnobsSettings, FioSettings, InfluxdbSettings
from magpie.environment.collector import InfluxDBCollector
from magpie.environment.lustre.lustre_controller import LustreController
from magpie.environment.lustre.lustre_env import LustreEnvironment
from magpie.environment.reward import SingleTuning2ProportionMetricsReward, SingleTuning3ProportionMetricsReward, \
    SingleTuning2ProportionMetricsRewardWithMovingAvg, DoubleTuning2ProportionMetricsReward
from magpie.environment.toy.toy_env import ToyEnvironment
from magpie.environment.toy.toy_knobs import ToyKnobs
from magpie.environment.toy.toy_performance_indicators import ToyPerformanceIndicators as TPI
from magpie.model.ddpg import DDPGSettings, DDPG
from magpie.model.dfs_model import DFSModel, DFSModelSettings
from magpie.model.ppo import PPOSettings, PPO
from magpie.types.dfs_configuration import ConfigurationScorePair
from magpie.types.distributed_file_system import DFS
from magpie.types.external_metrics import LustreExternalMetrics, ToyExternalMetrics
from magpie.types.rl_model import RLModel

logger = logging.getLogger(__name__)


def save_configuration_score_pairs(train_log_dir, configuration_score_lst: List[ConfigurationScorePair], name):
    file_path = train_log_dir + f"/{name}.txt"
    with open(file_path, "a") as f:
        f.write(pformat(configuration_score_lst))
        logger.info(f"persist {name} configurations to file {file_path}, configuration:{configuration_score_lst}")

def create_model(global_step, model: RLModel, tf_env: TFPyEnvironment) -> (DFSModel, DFSModelSettings):
    if model is RLModel.DDPG:
        model_settings = DDPGSettings(global_step=global_step)
        model = DDPG(tf_env, model_settings)
    elif model is RLModel.PPO:
        model_settings = PPOSettings(global_step=global_step)
        model = PPO(tf_env, model_settings)
    else:
        raise NotImplementedError
    return model, model_settings


def create_env(debug, dfs, enable_observation_normalizer, observation_time, reward_type,
               workload, model: RLModel, dd_workload=False, double_optimization=False):
    if dfs is DFS.LUSTRE:
        lustre_settings = LustreSettings()
        lustre_pis_settings = LustrePIsSettings()
        lustre_knobs_settings = LustreKnobsSettings()
        if workload is not None:
            fio_settings = FioSettings()
            fio_settings.workload = workload
        else:
            fio_settings = None
        internal_pis = lustre_pis_settings.file_system + lustre_pis_settings.cpu + lustre_pis_settings.ram
        knobs = lustre_knobs_settings.get_all_knobs()
        if double_optimization:
            if reward_type.num_args_return == 2:
                reward_model = DoubleTuning2ProportionMetricsReward(LustreExternalMetrics.get_throughput, reward_type, LustreExternalMetrics.get_iops)
            else:
                raise NotImplementedError
        else:
            if reward_type.num_args_return == 1:
                reward_model = SingleTuning2ProportionMetricsRewardWithMovingAvg(LustreExternalMetrics.get_throughput, tolerance_ratio=0.02)
            elif reward_type.num_args_return == 2:
                reward_model = SingleTuning2ProportionMetricsReward(LustreExternalMetrics.get_throughput, reward_type)
            elif reward_type.num_args_return == 3:
                reward_model = SingleTuning3ProportionMetricsReward(LustreExternalMetrics.get_throughput, reward_type)
            else:
                raise NotImplementedError
        controller = LustreController(lustre_settings)
        influxdb_settings = InfluxdbSettings()
        logger.info(f"lustre settings: {pformat(lustre_settings)}\n")
        logger.info(f"influxdb settings: {pformat(influxdb_settings)}\n")
        logger.info(f"fio settings: {pformat(fio_settings)}\n")
        collector = InfluxDBCollector(influxdb_settings, internal_pis)
        py_environment = LustreEnvironment(internal_pis, knobs, controller, collector, reward=reward_model,
                                           observation_time=observation_time, fio_settings=fio_settings,
                                           influxdb_settings=influxdb_settings,
                                           debug=debug,dd_workload=dd_workload)
    elif dfs is DFS.TOY:
        internal_pis = [i.value for i in [TPI.PI1, TPI.PI2]]
        knobs = [k.value for k in list(ToyKnobs)]
        if reward_type.num_args_return == 2:
            reward_model = SingleTuning2ProportionMetricsReward(ToyExternalMetrics.get_performance,
                                                                reward_type)
        elif reward_type.num_args_return == 3:
            reward_model = SingleTuning3ProportionMetricsReward(ToyExternalMetrics.get_performance,
                                                                reward_type)
        else:
            raise NotImplementedError
        py_environment = ToyEnvironment(internal_pis, knobs, reward_model,
                                        enable_observation_normalizer=enable_observation_normalizer,
                                        debug=debug)

    else:
        raise NotImplementedError
    if model is RLModel.PPO:
        py_environment = ActionClipWrapper(py_environment)
    tf_env = TFPyEnvironment(py_environment)
    return internal_pis, knobs, py_environment, tf_env


def evaluate_configuration(train_log_dir, top_configuration_score_lst: List[ConfigurationScorePair], tf_env,
                           evaluation_time):
    """
    evaluate configurations
    :param evaluation_time:
    :param top_configuration_score_lst:
    :return:
    """
    best_configuration_score = top_configuration_score_lst[0]
    evaluated_top_configurations = []
    for configuration_score in top_configuration_score_lst:
        new_config_score = tf_env.evaluate_configuration(configuration_score.configuration, evaluation_time)
        evaluated_top_configurations.append(new_config_score)
        logger.info(
            f"Best configuration under evaluation: {configuration_score}, new_score={new_config_score.score}")
        if best_configuration_score < new_config_score:
            best_configuration_score = new_config_score
    logger.info(f"Recommend configuration: {best_configuration_score}")
    save_configuration_score_pairs(train_log_dir, evaluated_top_configurations, "evaluated_good_configurations")
