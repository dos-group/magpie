import functools
from collections import defaultdict
from typing import List, Optional, Dict

import numpy as np
import tensorflow as tf
from tensorflow import Variable
from tf_agents.agents import tf_agent
from tf_agents.agents.ddpg import ddpg_agent
from tf_agents.agents.ddpg.actor_network import ActorNetwork
from tf_agents.agents.ddpg.critic_network import CriticNetwork
from tf_agents.environments import TFPyEnvironment
from tf_agents.keras_layers import inner_reshape
from tf_agents.networks import sequential, nest_map
from tf_agents.train.utils import spec_utils
from tf_agents.typing import types
from tf_agents.utils import common

from magpie.model.dfs_model import DFSModel, DFSModelSettings
from magpie.types.dfs_configuration import TuneParameter
from magpie.types.knob import Knob


class DDPGSettings(DFSModelSettings):
    actor_learning_rate: float = 1e-4
    critic_learning_rate: float = 1e-3
    actor_fc_layer_params: List[int] = [128, 128, 128]
    critic_obs_fc_layers: List[int] = (400,)
    critic_joint_fc_layers: List[int] = (300,)
    ou_stddev: float = 0.2
    ou_damping: float = 0.15
    target_update_tau: float = 0.05
    target_update_period: float = 5
    dqda_clipping: Optional[float] = None
    gamma: float = 0.995
    reward_scale_factor: float = 1.0
    gradient_clipping: Optional[float] = None
    debug_summaries: bool = False
    summarize_grads_and_vars: bool = True
    td_errors_loss_fn: Optional[types.LossFn] = tf.compat.v1.losses.huber_loss
    global_step: Variable


class DDPG(DFSModel):

    def __init__(self, environment: TFPyEnvironment, dfs_model_settings: DDPGSettings):
        super().__init__(environment, dfs_model_settings)

    def create_agent(self, environment: TFPyEnvironment, ddpg_settings: DDPGSettings) -> tf_agent.TFAgent:
        observation_spec, action_spec, time_step_spec = (spec_utils.get_tensor_specs(environment))
        actor_net = ActorNetwork(observation_spec, action_spec, fc_layer_params=ddpg_settings.actor_fc_layer_params)
        critic_net = CriticNetwork((observation_spec, action_spec),
                                   action_fc_layer_params=ddpg_settings.critic_obs_fc_layers,
                                   observation_fc_layer_params=ddpg_settings.critic_obs_fc_layers,
                                   joint_fc_layer_params=ddpg_settings.critic_joint_fc_layers)

        # actor_net = create_actor_network(ddpg_settings.actor_fc_layer_params, environment.action_spec())
        # critic_net = create_critic_network((400,),
        #                                    None,
        #                                    (300,))

        tf_agent = ddpg_agent.DdpgAgent(
            environment.time_step_spec(),
            environment.action_spec(),
            actor_network=actor_net,
            critic_network=critic_net,
            actor_optimizer=tf.compat.v1.train.AdamOptimizer(learning_rate=ddpg_settings.actor_learning_rate),
            critic_optimizer=tf.compat.v1.train.AdamOptimizer(learning_rate=ddpg_settings.critic_learning_rate),
            ou_stddev=ddpg_settings.ou_stddev,
            ou_damping=ddpg_settings.ou_damping,
            target_update_tau=ddpg_settings.target_update_tau,
            target_update_period=ddpg_settings.target_update_period,
            dqda_clipping=ddpg_settings.dqda_clipping,
            td_errors_loss_fn=ddpg_settings.td_errors_loss_fn,
            gamma=ddpg_settings.gamma,
            reward_scale_factor=ddpg_settings.reward_scale_factor,
            gradient_clipping=ddpg_settings.gradient_clipping,
            debug_summaries=ddpg_settings.debug_summaries,
            summarize_grads_and_vars=ddpg_settings.summarize_grads_and_vars,
            train_step_counter=ddpg_settings.global_step)
        return tf_agent

    def generate_knobs(self, knobs: List[Knob], action: np.array) -> Dict[str, List[TuneParameter]]:
        """
        generate knobs for given actions
        :param knobs:
        :param action:
        :return: {knob_scope, [Knob, Knob_value]}
        """
        new_config = defaultdict(list)
        for knob, action_value in zip(knobs, action):
            assert 0 <= action_value <= 1, "action value is between 0 and 1"
            if knob.type is np.int:
                new_value = knob.min + (knob.max - knob.min) * action_value
                new_value = int(new_value + 0.5)
            else:
                raise NotImplementedError(f"knob type {knob.type} is not implemented.")
            tune_parameter = TuneParameter(knob, new_value)
            new_config[knob.scope].append(tune_parameter)
        return new_config

    def create_actor_network(self, fc_layer_units, action_spec):
        """Create an actor network for DDPG."""
        flat_action_spec = tf.nest.flatten(action_spec)
        if len(flat_action_spec) > 1:
            raise ValueError('Only a single action tensor is supported by this network')
        flat_action_spec = flat_action_spec[0]
        dense = functools.partial(
            tf.keras.layers.Dense,
            activation=tf.keras.activations.relu,
            kernel_initializer=tf.compat.v1.variance_scaling_initializer(
                scale=1. / 3.0, mode='fan_in', distribution='uniform'))
        fc_layers = [dense(num_units) for num_units in fc_layer_units]

        num_actions = flat_action_spec.shape.num_elements()
        action_fc_layer = tf.keras.layers.Dense(
            num_actions,
            activation=tf.keras.activations.tanh,
            kernel_initializer=tf.keras.initializers.RandomUniform(
                minval=-0.003, maxval=0.003))

        scaling_layer = tf.keras.layers.Lambda(
            lambda x: common.scale_to_spec(x, flat_action_spec))
        return sequential.Sequential(fc_layers + [action_fc_layer, scaling_layer])

    def create_critic_network(self, obs_fc_layer_units,
                              action_fc_layer_units,
                              joint_fc_layer_units):
        """Create a critic network for DDPG."""
        dense = functools.partial(
            tf.keras.layers.Dense,
            activation=tf.keras.activations.relu,
            kernel_initializer=tf.compat.v1.variance_scaling_initializer(
                scale=1. / 3.0, mode='fan_in', distribution='uniform'))

        def split_inputs(inputs):
            return {'observation': inputs[0], 'action': inputs[1]}

        def create_fc_network(layer_units):
            return sequential.Sequential([dense(num_units) for num_units in layer_units])

        def create_identity_layer():
            return tf.keras.layers.Lambda(lambda x: x)

        obs_network = create_fc_network(
            obs_fc_layer_units) if obs_fc_layer_units else create_identity_layer()
        action_network = create_fc_network(
            action_fc_layer_units
        ) if action_fc_layer_units else create_identity_layer()
        joint_network = create_fc_network(
            joint_fc_layer_units) if joint_fc_layer_units else create_identity_layer(
        )
        value_fc_layer = tf.keras.layers.Dense(
            1,
            activation=None,
            kernel_initializer=tf.keras.initializers.RandomUniform(
                minval=-0.003, maxval=0.003))

        return sequential.Sequential([
            tf.keras.layers.Lambda(split_inputs),
            nest_map.NestMap({
                'observation': obs_network,
                'action': action_network
            }),
            nest_map.NestFlatten(),
            tf.keras.layers.Concatenate(),
            joint_network,
            value_fc_layer,
            inner_reshape.InnerReshape([1], [])
        ])

    def train(self, experience):
        return self.tf_agent.train(experience)
