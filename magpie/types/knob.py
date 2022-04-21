from typing import TypeVar, Generic

import numpy as np
from pydantic import root_validator
from pydantic.generics import GenericModel

T = TypeVar('T')


class Knob(GenericModel, Generic[T]):
    """
    DFS knob spec
    """
    name: str
    alias: str = None
    type: type
    # scope of the knob, e.g., the daemon type it applies to
    scope: str
    default: T
    min: T
    max: T

    def __hash__(self):
        scope = self.scope or ""
        return hash(self.name + scope)

    def __eq__(self, other):
        return (self.name, self.scope) == (other.name, other.scope)

    def __sstr__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_parameter_name(self):
        """
        parameter used in lustre setting
        :return:
        """
        return self.alias or self.name

    class Config:
        arbitrary_types_allowed = True

    @root_validator
    def check_numerical_range_validity(cls, values):
        if values.get("type") is np.bool:
            return values
        default, min, max = values.get("default"), values.get("min"), values.get("max")
        if min <= max and min <= default <= max:
            return values
        raise ValueError(f"knob settings is not valid, min={min}, default={default}, max={max} ")


class IntKnob(Knob[np.int]):
    """
    DFS integer knob spec
    """

    def __init__(self, **data) -> None:
        super().__init__(**data, type=np.int)
