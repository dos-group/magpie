from typing import List, Optional, Dict

import numpy as np
import tensorflow as tf
from pydantic import BaseSettings
from tensorflow import Variable
from tf_agents.agents import tf_agent
from tf_agents.environments import TFPyEnvironment
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.typing import types

from magpie.types.dfs_configuration import TuneParameter
from magpie.types.knob import Knob


class DFSModelSettings(BaseSettings):
    actor_learning_rate: float = 1e-4
    critic_learning_rate: float = 1e-3
    actor_fc_layer_params: List[int] = [128, 128, 128]
    gamma: float = 0.995
    reward_scale_factor: float = 1.0
    gradient_clipping: Optional[float] = None
    debug_summaries: bool = False
    summarize_grads_and_vars: bool = True
    replay_buffer_capacity: int = 1000
    td_errors_loss_fn: Optional[types.LossFn] = tf.compat.v1.losses.huber_loss
    global_step: Variable


class DFSModel:
    """
    DFS model
    """

    def __init__(self, environment: TFPyEnvironment, dfs_model_settings: DFSModelSettings):
        self.environment = environment
        self.tf_agent = self.create_agent(environment, dfs_model_settings)
        self.tf_agent.initialize()
        self.replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
            self.tf_agent.collect_data_spec,
            batch_size=environment.batch_size,
            max_length=dfs_model_settings.replay_buffer_capacity)

    def create_agent(self, environment: TFPyEnvironment, dfs_model_settings: DFSModelSettings) -> tf_agent.TFAgent:
        raise NotImplementedError

    def generate_knobs(self, knobs: List[Knob], action: np.array) -> Dict[str, List[TuneParameter]]:
        """
        generate knobs for given actions
        :param knobs:
        :param action:
        :return: {knob_scope, [Knob, Knob_value]}
        """
        raise NotImplementedError

    def get_dataset_iterator(self, num_parallel_calls, sample_batch_size, num_steps, prefetch_size):
        dataset = self.replay_buffer.as_dataset(
            num_parallel_calls=num_parallel_calls,
            sample_batch_size=sample_batch_size,
            num_steps=num_steps).prefetch(prefetch_size)
        return iter(dataset)

    def train(self, experience):
        return self.tf_agent.train(experience)
