from magpie.types.str_enum import StrEnum


class RLModel(StrEnum):
    """
    RL models enum
    """
    PPO = "ppo"
    DDPG = "ddpg"
