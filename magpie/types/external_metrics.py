from typing import Dict


class ExternalMetrics(object):
    """
    External Metrics used by RL agent as reward function input
    """

    def __lt__(self, other):
        raise NotImplementedError

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def get_all_metrics(self) -> Dict[str, float]:
        return self.__dict__


class ToyExternalMetrics(ExternalMetrics):

    def __init__(self, performance):
        self.performance = performance

    @staticmethod
    def get_performance(self):
        return self.performance

    def __lt__(self, other):
        return self.performance < other.performance


class LustreExternalMetrics(ExternalMetrics):

    def __init__(self, throughput, iops):
        self.throughput = throughput
        self.iops = iops

    @staticmethod
    def get_iops(self):
        return self.iops

    @staticmethod
    def get_throughput(self):
        return self.throughput

    def __lt__(self, other):
        return self.throughput < other.throughput
