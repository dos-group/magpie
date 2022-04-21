import os
from typing import List, Optional

from pydantic import BaseSettings

from magpie.environment.lustre.lustre_knobs import LustreKnobs
from magpie.environment.lustre.lustre_performance_indicators import LustrePerformanceIndicators as LPI
from magpie.types.knob import Knob
from magpie.types.performance_indicator import FloatPerformanceIndicator
from magpie.types.workload import Workload
from magpie.utils.commons import APP_ROOT

# the folder used to tune stripe size and stripe count
STRIPE_TUNING_FOLDER: Optional[str] = "/mnt/lustrefs/offline_tuning/"

class AppSettings(BaseSettings):
    class Config:
        env_file = os.getenv("PYDANTIC_ENV_FILE")
        env_file_encoding = 'utf-8'



class WorkloadSettings(AppSettings):
    ssh_user: str
    ssh_node: str

class FioSettings(WorkloadSettings):
    # the fio script path on the server
    fio_script_path: str = "./app/magpie/magpie/scripts/start_fio.sh"
    fio_conf_folder: str = "/home/houkun.zhu/app/magpie/magpie/config/fio"
    local_fio_conf_folder: str = APP_ROOT + "/config/fio"
    workload: Optional[Workload]

class InfluxdbSettings(AppSettings):
    url: str
    token: str
    org: str = "magpie"
    magpie_bucket: str = "magpie"



class LustreSettings(AppSettings):
    # osc hosts
    osc_nodes: List[str]
    # osd hosts
    osd_nodes: List[str]
    # mds hosts
    mds_nodes: List[str]
    # ssh user
    ssh_user: str = "houkun.zhu"


class LustrePIsSettings(AppSettings):
    """
    Configure Lustre Performance Indicators used by models
    """
    # file system related metrics
    file_system: List[FloatPerformanceIndicator] = [
        LPI.CUR_DIRTY_BYTES.value, LPI.CUR_GRANT_BYTES.value,
        LPI.READ_RPCS_IN_FLIGHT.value, LPI.WRITE_RPCS_IN_FLIGHT.value,
        LPI.PENDING_READ_PAGES.value, LPI.PENDING_WRITE_PAGES.value,
        LPI.CACHE_HIT_RATIO.value
    ]
    # cpu related metrics
    cpu: List[FloatPerformanceIndicator] = [LPI.USAGE_IDLE.value, LPI.USAGE_IOWAIT.value]
    # ram related metrics
    ram: List[FloatPerformanceIndicator] = [LPI.RAM_USED_PERCENT.value]

    query_file: str = APP_ROOT + "/config/lustre_influxdb.flux"


class LustreKnobsSettings(AppSettings):
    """
    Configure Lustre Knobs to be tuned by Magpie
    """
    osc: List[Knob] = [
        # LustreKnobs.MAX_DIRTY_MB.knob, LustreKnobs.MAX_RPCS_IN_FLIGHT.knob,
        # LustreKnobs.MAX_PAGES_PER_RPC.knob, LustreKnobs.MAX_CACHED_MB.knob,
        # LustreKnobs.MAX_READ_AHEAD_MB.knob,
        # LustreKnobs.MAX_READ_AHEAD_WHOLE_MB.knob,
        # LustreKnobs.STATHEAD_MAX.knob
        # LustreKnobs.CHECKSUM_PAGES.knob
    ]

    osd: List[Knob] = [
        # LustreKnobs.MAX_OST_THREADS.knob, LustreKnobs.BRW_SIZE.knob,
        # LustreKnobs.MAX_OST_IO_THREADS.knob, LustreKnobs.MAX_OST_CREATE_THREADS.knob
    ]
    mds: List[Knob] = [
        # LustreKnobs.MAX_MDS_THREADS.knob, LustreKnobs.MAX_MDS_READPAGE_THREADS.knob,
        # LustreKnobs.MAX_MDS_SETATTR_THREADS.knob
    ]

    offline: List[Knob] = [
        LustreKnobs.STRIPE_SIZE.knob, LustreKnobs.STRIPE_COUNT.knob
    ]

    def get_all_knobs(self):
        return self.osc + self.osd + self.mds + self.offline
