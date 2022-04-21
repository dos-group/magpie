from enum import Enum

from magpie.types.knob import IntKnob, Knob


class LustreKnobs(Enum):
    """
    lustre knobs
    """

    def __new__(cls, knob: Knob):
        # value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj.knob = knob
        obj._value_ = knob.name
        return obj

    MAX_DIRTY_MB = IntKnob(name="max_dirty_mb", scope="osc", min=1, max=2047, default=10)
    # 39.4.5.1. Configuring the Client Metadata RPC Stream
    MAX_RPCS_IN_FLIGHT = IntKnob(name="max_rpcs_in_flight", scope="osc", min=1, max=256, default=8)

    MAX_PAGES_PER_RPC = IntKnob(name="max_pages_per_rpc", scope="osc", min=1, max=4096, default=1024)
    # 39.4.2.1. Tuning File Readahead
    MAX_CACHED_MB = IntKnob(name="max_cached_mb", scope="osc.llite", min=2048, max=12288, default=8192)
    MAX_READ_AHEAD_MB = IntKnob(name="max_read_ahead_mb", scope="osc.llite", min=64, max=7929, default=64)
    MAX_READ_AHEAD_WHOLE_MB = IntKnob(name="max_read_ahead_whole_mb", scope="osc.llite", min=1, max=64, default=4)
    # MAX_READ_AHEAD_PER_FILE_MB = IntKnob(name="max_read_ahead_per_file_mb", scope="osc.llite", min=1, max=6929, default=4)

    STATHEAD_MAX = IntKnob(name="statahead_max", scope="osc.llite", min=0, max=8192, default=32)
    # Controls the maximum amount of data readahead on all files.
    # needs to be not bigger than max_read_ahead_mb

    # disable checksum can increase performance
    # flag to enable/disable checksum
    CHECKSUM_PAGES = IntKnob(name="checksum_pages", scope="osc.llite", min=0, max=1, default=1)

    MAX_MDS_THREADS = IntKnob(name="max_mds_threads", alias="mds.MDS.mdt.threads_max", scope="mds", min=256, max=1024,
                              default=256)
    MAX_MDS_READPAGE_THREADS = IntKnob(name="max_mds_readpage_threads", alias="mds.MDS.mdt_readpage.threads_max",
                                       scope="mds",
                                       min=112, max=1024, default=112)
    MAX_MDS_SETATTR_THREADS = IntKnob(name="max_mds_setattr_threads", alias="mds.MDS.mdt_setattr.threads_max",
                                      scope="mds",
                                      min=112, max=1024, default=112)

    MAX_OST_THREADS = IntKnob(name="max_ost_threads", alias="ost.OSS.ost.threads_max", scope="oss", min=168, max=512,
                              default=168)
    # BRW_SIZE = IntKnob(name="brw_size", alias="obdfilter.*.brw_size", scope="oss", min=4, max=16, default=4)
    MAX_OST_IO_THREADS = IntKnob(name="max_ost_io_threads", alias="ost.OSS.ost_io.threads_max", scope="oss", min=168,
                                 max=512,
                                 default=168)
    MAX_OST_CREATE_THREADS = IntKnob(name="max_ost_create_threads", alias="ost.OSS.ost_create.threads_max", scope="oss",
                                     min=24,
                                     max=512,
                                     default=24)

    STRIPE_COUNT = IntKnob(name="stripe_count", alias="lfs setstripe -c ", scope="stripe",
                           min=1,
                           max=10,
                           default=1)
    STRIPE_SIZE = IntKnob(name="stripe_size", alias="lfs setstripe -S", scope="stripe",
                          min=1,
                          max=1024,
                          default=16)
    def __str__(self):
        return self.value.name
