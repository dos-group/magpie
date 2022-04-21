import logging
import os

from magpie.config.config import WorkloadSettings, STRIPE_TUNING_FOLDER, FioSettings
from magpie.types.workload import Workload
from magpie.utils.cmd_utils import exec_remote_cmd
from magpie.utils.fio_utils import FioUtils


class DDUtils:
    """
    DD workload utils
    """
    def __init__(self, dd_settings: WorkloadSettings):

        self.logger = logging.Logger(__name__)
        self.ssh_user = dd_settings.ssh_user
        self.ssh_node = dd_settings.ssh_node
        settings = FioSettings()
        self.fio_utils = FioUtils(settings)
        self.type = "filebench"
        self.logger.info(f"DDUtils is runing on type {self.type}")

    def clean(self):
        cmd = f"sudo rm -rf {STRIPE_TUNING_FOLDER}/*"
        exec_remote_cmd(self.ssh_user, self.ssh_node, cmd)

    def start_workload(self, block_size="1M", count=500, eval=False):
        # start fio environment and kill existing fio process
        # executed in detach mode by adding option -d

        if self.type == "fio":
            self.fio_utils.start_workload(workload=Workload.SEQUENTIAL_1M_50PCT_WRITE_5_JOBS, detach=False)
        elif self.type == "filebench":
            workload_name = os.environ['WORKLOAD_NAME']
            if workload_name is None or workload_name == "":
                raise AttributeError("WORKLOAD_NAME env variable is not set")
            self.logger.info(f"Using workload {workload_name}.")
            # workload_name = "videoserver.f"
            if eval:
                workload_name = f"eval_{workload_name}"
            cmd = f"mpirun -hostfile /home/houkun.zhu/app/fb_workload/mpi_host.txt sudo /usr/local/bin/filebench -f /home/houkun.zhu/app/fb_workload/{workload_name}"
            self.logger.info(f"start workload {cmd}")
            result = exec_remote_cmd(self.ssh_user, self.ssh_node, cmd)
            self.logger.info(result)
        else:
            raise NotImplementedError
