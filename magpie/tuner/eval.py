import logging
from pathlib import Path

import tensorflow as tf
import typer
from tf_agents.policies import tf_policy
from tf_agents.utils import common

from magpie.config.config import FioSettings
from magpie.environment.controller import logger
from magpie.types.distributed_file_system import DFS
from magpie.types.reward_type import RewardType
from magpie.types.rl_model import RLModel
from magpie.types.workload import Workload
from magpie.utils import magpie_logging
from magpie.utils.fio_utils import FioUtils
from magpie.utils.tuner_utils import create_model, create_env


class Evaluation:
    """
    model evaluation
    """
    logger = logging.getLogger(__name__)

    def __init__(self, tf_env, policy: tf_policy.TFPolicy, num_eval_iterations, fio_settings: FioSettings):
        self.tf_env = tf_env
        self.py_env = self.tf_env.pyenv.envs[0]
        good_configurations = self.py_env.good_configurations
        self.init_time_step = tf_env.reset()
        self.py_env.good_configurations = good_configurations
        self.init_external_metrics = self.tf_env.get_info().item().get_all_metrics()
        self.policy = policy
        self.num_eval_iterations = num_eval_iterations
        self.fio_settings = fio_settings



    def test(self):
        time_step = self.init_time_step
        good_configurations = self.py_env.good_configurations
        logger.info(f"good configurations:{good_configurations}")
        for iter_no in range(self.num_eval_iterations):
            action_step = self.policy.action(time_step)
            time_step = self.tf_env.step(action_step.action)
            external_metrics = self.tf_env.get_info()

            performance_improvement = ""
            for k, v in external_metrics.item().get_all_metrics().items():
                init_v = self.init_external_metrics[k]
                improve_pct = v / init_v * 100 if init_v != 0 else 0
                performance_improvement += f"{k}={improve_pct:.2f}%"
            logger.info(
                f"eval iteration[{iter_no}], performance improvement: {performance_improvement}%, raw data:{external_metrics}")
            good_configurations = self.py_env.good_configurations
            logger.info(f"good configurations:{good_configurations}")
        good_configurations = self.py_env.good_configurations
        logger.info(f"good configuration {good_configurations}")


def eval(self):
        fio_utils = FioUtils(self.fio_settings)
        # set the parameter

        fio_utils.benchmark()


def main(reward_type: RewardType = typer.Option(..., help="reward function type"),
         observation_time: int = typer.Option(..., help="Observation time after each action"),
         debug: bool = typer.Option(False, help="debug flag"),
         rl_model: RLModel = typer.Option(RLModel.DDPG.value, help="RL model"),
         num_eval_iteration: int = typer.Option(10, help="number of evaluation iterations"),
         checkpoint_dir: Path = typer.Option(..., help="checkpoint path to evaluate"),
         # workload: Workload = typer.Option(..., help="workload"),
         dfs: DFS = typer.Option(DFS.LUSTRE.value, help="distributed file system type"),
         enable_observation_normalizer: bool = typer.Option(False, help="Normalize observation"),
         dd_workload: bool = typer.Option(False, help="flag to use DD workload")
         ):

    workload = Workload.FINAL_RW if not dd_workload else None
    _, _, _, env = create_env(debug, dfs, enable_observation_normalizer, observation_time, reward_type, workload, rl_model, dd_workload=dd_workload)
    global_step = tf.compat.v1.train.get_or_create_global_step()
    tf.summary.experimental.set_step(global_step)
    model, model_settings = create_model(global_step, rl_model, env)
    eval_checkpointer = common.Checkpointer(
        ckpt_dir=checkpoint_dir,
        max_to_keep=10,
        agent=model.tf_agent,
        policy=model.tf_agent.policy,
        replay_buffer=model.replay_buffer,
        global_step=global_step
    )
    eval_checkpointer.initialize_or_restore()
    fio_settings = FioSettings()
    fio_settings.workload = workload
    Evaluation(env, model.tf_agent.policy, num_eval_iteration, fio_settings).test()
    logger.info("finish evaluation")


if __name__ == "__main__":
    magpie_logging.init()
    typer.run(main)
