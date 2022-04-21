import logging
import subprocess

import requests

logger = logging.getLogger(__name__)


def exec_cmd_by_rest(node, cmd):
    url = f"http://{node}:5000/execute"
    data = {"cmd": cmd}
    res = requests.get(url, params=data)
    if res.status_code != 200 or "error" in res.text:
        logger.error(f"Cmd execution error,node:{node}, cmd:{cmd}, result:{res.text}")
    return res.text


def exec_cmd(cmd, get_all_result=False, raise_error=True):
    """
    execute command
    :param cmd: str|list
    :param get_all_result:
    :param raise_error:
    :return: standard output if return code is 0, otherwise raise RuntimeError
    """
    if type(cmd) is str:
        result = subprocess.run(["/bin/bash", "-c", cmd], capture_output=True, text=True)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and raise_error is True:
        raise RuntimeError(f"Command {cmd} execution error, {result.stdout}, {result.stderr}")
    else:
        logger.debug(f"Command \"{cmd}\" result, stdout={result.stdout}, stderr={result.stderr}")
        if get_all_result:
            return result
        else:
            return result.stdout.strip()


def exec_remote_cmd(ssh_user, hostname, cmd):
    """
    execute remote command
    :param ssh_user: ssh user
    :param hostname:
    :param cmd:
    :return:
    """
    cmd = f"ssh {ssh_user}@{hostname} \"{cmd}\""
    return exec_cmd(cmd)
