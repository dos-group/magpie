from typing import Text

import numpy as np
import tensorflow as tf
from tf_agents.metrics import py_metric, tf_py_metric
from tf_agents.trajectories import trajectory as traj
from tf_agents.utils import numpy_storage, nest_utils


class SumReturnMetric(py_metric.PyStepMetric):
    def __init__(self, name: Text = 'SumReturnMetric'):
        super(SumReturnMetric, self).__init__(name)
        self._np_state = numpy_storage.NumpyState()
        self.reset()

    def reset(self):
        self._np_state.reward_sum = np.float32(0)

    def result(self) -> np.int64:
        return self._np_state.reward_sum

    def call(self, trajectory: traj.Trajectory):
        if trajectory.step_type.ndim == 0:
            trajectory = nest_utils.batch_nested_array(trajectory)
        self._np_state.reward_sum += trajectory.reward[0]


class TFSumReturnMetric(tf_py_metric.TFPyMetric):

    def __init__(self, name='TFSumReturnMetric', dtype=tf.float32):
        py_metric = SumReturnMetric()

        super(TFSumReturnMetric, self).__init__(
            py_metric=py_metric, name=name, dtype=dtype)
