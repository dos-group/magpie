from unittest import TestCase

from magpie.utils.cmd_utils import exec_cmd_by_rest


class Test(TestCase):
    def test_exec_cmd_by_rest(self):
        rest = exec_cmd_by_rest("wally033", "sudo lctl get_param osc.*.max_rpcs_in_flight && sudo lctl list_param osc.*.*")
        print(rest)
