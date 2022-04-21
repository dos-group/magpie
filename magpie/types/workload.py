from enum import Enum
from typing import NamedTuple, Optional


class Body(NamedTuple):
    io_type: str
    block_size: str
    read_pct: Optional[str] = None
    num_jobs: int = 20
    runtime: str = "48h"
    template: str = "fio_template.conf"
    output_dir: str = "/mnt/lustrefs/fio/"


class Workload(Body, Enum):

    # def __new__(cls, io_type, block_size, read_pct=None, num_jobs=20, runtime="48h", template="fio.conf",
    #             output_dir="/mnt/lustrefs/fio/"):
    #     obj = object.__new__(cls)
    #     obj.io_type = io_type
    #     obj.block_size = block_size
    #     obj.read_pct = read_pct
    #     obj.num_jobs = num_jobs
    #     obj.runtime = runtime
    #     obj.template = template
    #     obj.output_dir = output_dir
    #
    #     if read_pct is not None:
    #         obj._value_ = f"{io_type}_{block_size}_{read_pct}_read"
    #     else:
    #         obj._value_ = f"{io_type}_{block_size}"
    #     obj._name_ = obj._value_
    #     return obj

    def __str__(self):
        return self._name_.lower()

    def __repr__(self):
        return "<%s.%s: %s>" % (
            self.__class__.__name__, self._name_, self._value_)

    def to_fio_params(self):
        if self.read_pct is not None:
            return f"--rw={self.io_type} --bs={self.block_size} --rwmixread={self.read_pct}"
        else:
            return f"--rw={self.io_type} --bs={self.block_size}"

    RANDOM_4K_10PCT_READ = Body("randrw", "4k", read_pct="10")
    RANDOM_4K_90PCT_READ = Body("randrw", "4k", read_pct="90")
    RANDOM_10M_10PCT_READ = Body("randrw", "10m", read_pct="10")
    RANDOM_10M_90PCT_READ = Body("randrw", "10m", read_pct="90")
    RANDOM_1M_10PCT_READ = Body("randrw", "1m", read_pct="10")
    RANDOM_1M_90PCT_READ = Body("randrw", "1m", read_pct="90")
    SEQUENTIAL_4K_10PCT_READ = Body("rw", "4k", read_pct="10")
    SEQUENTIAL_4K_90PCT_READ = Body("rw", "4k", read_pct="90")
    SEQUENTIAL_1M_10PCT_READ = Body("rw", "1m", read_pct="10")
    SEQUENTIAL_1M_90PCT_READ = Body("rw", "1m", read_pct="90")
    RANDOM_1M_WRITE = Body("randwrite", "1m")
    RANDOM_1M_READ = Body("randread", "1m")
    RANDOM_4K_WRITE = Body("randwrite", "4k")
    RANDOM_4K_READ = Body("randread", "4k")

    SEQUENTIAL_1M_50PCT_WRITE_10_JOBS = Body(io_type="rw", read_pct="50", block_size="1m", num_jobs=10)
    SEQUENTIAL_1M_50PCT_WRITE_5_JOBS = Body(io_type="rw", read_pct="50", block_size="1m", num_jobs=5)
    SEQUENTIAL_EXPLORATION = Body(io_type="rw", read_pct="50", block_size="1m", num_jobs=5, template="fio_explore.conf")

    MULTI_SMALL_FILES = Body(io_type="rw", read_pct="50", block_size="1m", num_jobs=5, template="fio_small_files.conf")
    FINAL_WRITE = Body(io_type="write", block_size="1m", num_jobs=10)
    FINAL_READ = Body(io_type="read", block_size="1m", num_jobs=10)
    FINAL_RW = Body(io_type="rw", read_pct="50",  block_size="1m", num_jobs=10)


    SEQUENTIAL_10M_WRITE_10_JOBS = Body(io_type="write", block_size="10m", num_jobs=10)
    SEQUENTIAL_10M_WRITE_20_JOBS = Body(io_type="write", block_size="10m", num_jobs=20)
    SEQUENTIAL_1M_WRITE_10_JOBS = Body(io_type="write", block_size="1m", num_jobs=10)
    SEQUENTIAL_1M_WRITE_20_JOBS = Body(io_type="write", block_size="1m", num_jobs=20)
    SEQUENTIAL_256K_WRITE_10_JOBS = Body(io_type="write", block_size="256k", num_jobs=10)
    SEQUENTIAL_256K_WRITE_20_JOBS = Body(io_type="write", block_size="256k", num_jobs=20)
    SEQUENTIAL_4k_WRITE_10_JOBS = Body(io_type="write", block_size="4k", num_jobs=10)
    SEQUENTIAL_4k_WRITE_20_JOBS = Body(io_type="write", block_size="4k", num_jobs=20)

    SEQUENTIAL_10M_READ_10_JOBS = Body(io_type="read", block_size="10m", num_jobs=10)
    SEQUENTIAL_10M_READ_20_JOBS = Body(io_type="read", block_size="10m", num_jobs=20)
    SEQUENTIAL_1M_READ_10_JOBS = Body(io_type="read", block_size="1m", num_jobs=10)
    SEQUENTIAL_1M_READ_20_JOBS = Body(io_type="read", block_size="1m", num_jobs=20)
    SEQUENTIAL_256K_READ_10_JOBS = Body(io_type="read", block_size="256k", num_jobs=10)
    SEQUENTIAL_256K_READ_20_JOBS = Body(io_type="read", block_size="256k", num_jobs=20)
    SEQUENTIAL_4k_READ_10_JOBS = Body(io_type="read", block_size="4k", num_jobs=10)
    SEQUENTIAL_4k_READ_20_JOBS = Body(io_type="read", block_size="4k", num_jobs=20)


