from unittest import TestCase

from magpie.utils import tuner_utils


class Test(TestCase):
    def test_save_configuration_score_pairs(self):
        tuner_utils.save_configuration_score_pairs("/Users/diskun/Work/Workspace/Python/Magpie/magpie/log/train", ["fds"], "best")
