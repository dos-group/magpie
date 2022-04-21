from collections import defaultdict
from typing import List

from magpie.config.config import LustreSettings, STRIPE_TUNING_FOLDER
from magpie.environment.controller import DistributedDFSController, logger
from magpie.environment.lustre.lustre_knobs import LustreKnobs
from magpie.types.dfs_configuration import TuneParameter, ScopedTuneParameters
from magpie.types.knob import Knob
from magpie.utils.cmd_utils import exec_cmd_by_rest


class LustreController(DistributedDFSController):
    """
    Lustre Controller
    """

    def __init__(self, lustre_settings: LustreSettings):
        self.lustre_settings = lustre_settings
        self.ssh_user = lustre_settings.ssh_user

    def _set_scope_params(self, scoped_parameters: ScopedTuneParameters):
        cmds = []
        if "osc" in scoped_parameters.scope:
            nodes = self.lustre_settings.osc_nodes
            svc = scoped_parameters.scope.split(".")[-1]
            for tune_param in scoped_parameters.parameters:
                cmds.append(f"sudo lctl set_param {svc}.*.{tune_param.name.name} {tune_param.value}")
            cmd = " && ".join(cmds)
        elif scoped_parameters.scope == "osd" or scoped_parameters.scope == "osc" or scoped_parameters.scope == "oss":
            nodes = self.lustre_settings.osd_nodes
            for tune_param in scoped_parameters.parameters:
                if tune_param.name.alias is not None:
                    cmds.append(f"sudo lctl set_param {tune_param.name.alias} {tune_param.value}")
                else:
                    cmds.append(f"sudo lctl set_param osd.*.{tune_param.name.name} {tune_param.value}")
            cmd = " && ".join(cmds)
        elif scoped_parameters.scope == "mds":
            nodes = self.lustre_settings.mds_nodes
            for tune_param in scoped_parameters.parameters:
                if "threads_max" in tune_param.name.get_parameter_name():
                    cmds.append(f"sudo lctl set_param {tune_param.name.get_parameter_name()} {tune_param.value}")
                else:
                    raise NotImplementedError
            cmd = " && ".join(cmds)
        elif scoped_parameters.scope == "stripe":
            cmd = "sudo lfs setstripe --stripe-index 0"
            nodes = [self.lustre_settings.osc_nodes[0]]
            for tune_param in scoped_parameters.parameters:
                if tune_param.name == LustreKnobs.STRIPE_COUNT.knob:
                    cmd += f" -c {tune_param.value}"
                elif tune_param.name == LustreKnobs.STRIPE_SIZE.knob:
                    multiple_of_64 = tune_param.value
                    value = multiple_of_64 * 64
                    cmd += f" -S {value}K"
                else:
                    raise NotImplementedError(f"Unrecognized param {tune_param}")
            cmd += f" {STRIPE_TUNING_FOLDER}"
        else:
            raise NotImplementedError(scoped_parameters.scope)
        if nodes is None or len(nodes) == 0:
            logger.warning(f"no nodes is setting for {scoped_parameters.scope}!")
        for node in nodes:
            # exec_remote_cmd(self.ssh_user, node, cmd)
            res = exec_cmd_by_rest(node, cmd)
            logger.debug(f"node:{node}, cmd: {cmd}, res:{res}")

    def reset_params(self, tuned_params: List[Knob]):
        new_config = defaultdict(list)
        for knob in tuned_params:
            tune_parameter = TuneParameter(knob, knob.default)
            new_config[knob.scope].append(tune_parameter)
        scope_param_lst = [ScopedTuneParameters(scope=scope, parameters=params) for scope, params in new_config.items()]
        for scope_param in scope_param_lst:
            self.set_params(scope_param)
        logger.info("Successfully reset parameters.")
