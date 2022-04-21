from typing import Generic, TypeVar

import numpy as np
from pydantic import BaseModel

T = TypeVar('T')


class PerformanceIndicator(BaseModel, Generic[T]):
    """
    DFS performance indicator
    """
    name: str
    # alias used if name is different in InfluxDB
    alias: str = None
    type: type = type(T)
    description: str = None

    def __hash__(self):
        return hash((self.name))

    def __eq__(self, other):
        return (self.name) == (other.name)


class FloatPerformanceIndicator(PerformanceIndicator[np.float]):
    """
    DFS float type performance indicator
    """
    min: T
    max: T
