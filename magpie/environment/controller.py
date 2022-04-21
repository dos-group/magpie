import logging
from collections import defaultdict
from typing import List, Union

from magpie.types.dfs_configuration import ScopedTuneParameters, TuneParameter
from magpie.types.knob import Knob

logger = logging.getLogger(__name__)


class CentralDFSController:
    """
    Controller for DFS with a central parameter management system. e.g., CephFS.
    """

    def set_params(self, scoped_parameters: ScopedTuneParameters, **kwargs):
        """
        set parameters in corresponding daemon
        :param scoped_parameters:
        :param kwargs:
        :return:
        """
        raise NotImplementedError


class DistributedDFSController:
    """
    Controller for DFS in which configuration can be only set in each daemon. e.g., Lustre.
    """

    def set_params(self, parameters: Union[ScopedTuneParameters, List[TuneParameter]], **kwargs):
        """
        set parameters in corresponding daemon
        :param parameters:
        :param kwargs:
        :return:
        """
        if type(parameters) is list:
            scope_param_lst = self._list_to_scope(parameters)
            for scope_param in scope_param_lst:
                self._set_scope_params(scope_param)
        else:
            self._set_scope_params(parameters)

    def _set_scope_params(self, parameters: ScopedTuneParameters):
        raise NotImplementedError

    def _list_to_scope(self, parameter_list: List[TuneParameter]) -> List[ScopedTuneParameters]:
        """
        convert parameter list to dict of ScopedTuneParameters
        :param parameter_list:
        :return: dict of ScopedTuneParameters
        """
        res = defaultdict(list)
        for parameter in parameter_list:
            res[parameter.name.scope].append(parameter)
        return [ScopedTuneParameters(scope, scope_param) for scope, scope_param in res.items()]

    def reset_params(self, tuned_params: List[Knob]):
        """
        reset DFS tuned parameters to default value
        :param tuned_params:
        :return:
        """
        raise NotImplementedError
