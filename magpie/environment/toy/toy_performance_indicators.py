from enum import Enum

from magpie.types.performance_indicator import FloatPerformanceIndicator


class ToyPerformanceIndicators(Enum):
    # toy FS
    PI1 = FloatPerformanceIndicator(name="pi1", description="performance indicator 1", min=0, max=1000)
    PI2 = FloatPerformanceIndicator(name="pi2", description="performance indicator 2", min=0, max=100)
    PI3 = FloatPerformanceIndicator(name="metric", description="metrics to tune", min=0, max=2e8)
