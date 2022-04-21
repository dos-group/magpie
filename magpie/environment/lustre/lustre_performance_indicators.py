from enum import Enum

from magpie.types.performance_indicator import FloatPerformanceIndicator


class LustrePerformanceIndicators(Enum):
    # Lustre FS
    READ_BYTES_RATE = FloatPerformanceIndicator(name="read_bytes_rate", alias="read_bytes",
                                                description="read throughput in bytes/s", min=0,
                                                max=2e8)
    WRITE_BYTES_RATE = FloatPerformanceIndicator(name="write_bytes_rate", alias="write_bytes",
                                                 description="write throughput in bytes/s",
                                                 min=0, max=2e8)
    READ_IOPS_RATE = FloatPerformanceIndicator(name="read_iops_rate", alias="read_calls", description="read iops",
                                               min=0, max=1000)
    WRITE_IOPS_RATE = FloatPerformanceIndicator(name="write_iops_rate", alias="write_calls", description="write iops",
                                                min=0, max=1000)
    CUR_DIRTY_BYTES = FloatPerformanceIndicator(name="cur_dirty_bytes", description="current dirty bytes", min=0,
                                                max=2e8)
    CUR_GRANT_BYTES = FloatPerformanceIndicator(name="cur_grant_bytes", description="current grant bytes", min=0,
                                                max=2e8)
    READ_RPCS_IN_FLIGHT = FloatPerformanceIndicator(name="read_rpcs_in_flight", description="read rpcs in flight",
                                                    min=0, max=256 * 4)
    WRITE_RPCS_IN_FLIGHT = FloatPerformanceIndicator(name="write_rpcs_in_flight", description="write rpcs in flight",
                                                     min=0, max=256 * 4)
    PENDING_READ_PAGES = FloatPerformanceIndicator(name="pending_read_pages", description="pending read pages", min=0,
                                                   max=2e8)
    PENDING_WRITE_PAGES = FloatPerformanceIndicator(name="pending_write_pages", description="pending write pages",
                                                    min=0, max=2e8)
    CACHE_HIT_RATIO = FloatPerformanceIndicator(name="cache_hit_ratio",
                                                description="cache hit ratio (cache_hit/cache_access)", min=0, max=1)
    # CACHE_ACCESS = FloatPerformanceIndicator(name="cache_access", min=0, max=2e8)
    # CACHE_MISS = FloatPerformanceIndicator(name="cache_miss", min=0, max=2e8)

    # CPU
    USAGE_IDLE = FloatPerformanceIndicator(name="usage_idle", min=0, max=100)
    USAGE_IOWAIT = FloatPerformanceIndicator(name="usage_iowait", min=0, max=100)

    # RAM
    RAM_USED_PERCENT = FloatPerformanceIndicator(name="used_percent", min=0, max=100)

    def get_alias_or_name(self):
        """
        get alias or name of the PI, used in InfluxDB to fetch corresponding PIs
        :return:
        """
        return self.value.alias or self.value.name