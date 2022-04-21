import logging

from magpie.config.config import FioSettings
from magpie.utils.cmd_utils import exec_remote_cmd, exec_cmd

logger = logging.Logger(__name__)


class FioUtils:
    def __init__(self, fio_settings: FioSettings):
        self.fio_script_path = fio_settings.fio_script_path
        self.workload = fio_settings.workload
        self.fio_conf_folder = fio_settings.fio_conf_folder
        self.local_fio_conf_folder = fio_settings.local_fio_conf_folder
        self.ssh_user = fio_settings.ssh_user
        self.ssh_node = fio_settings.ssh_node

    def benchmark(self):
        # run fio
        fio_exec_cmd = f"sh {self.fio_script_path}"
        benchmark_result = exec_remote_cmd(self.ssh_user, self.ssh_node, fio_exec_cmd)
        logger.info(benchmark_result)
        return benchmark_result

    def generate_fio_conf(self, workload):
        with open(self.local_fio_conf_folder + "/" + workload.template) as f:
            generated_fio_conf = f.read() \
                .replace("NUMBER_JOBS", workload.num_jobs.__str__()) \
                .replace("OUTPUT_DIR", workload.output_dir) \
                .replace("IO_TYPE", workload.io_type) \
                .replace("BLOCK_SIZE", workload.block_size)
        local_generated_file = self.local_fio_conf_folder + "/" + "fio_generated.conf"
        remote_generated_file_path = self.fio_conf_folder + "/" + "fio_generated.conf"
        with open(local_generated_file, "w") as f:
            f.write(generated_fio_conf)
        # copy generated file to remote
        exec_cmd(f"scp {local_generated_file} {self.ssh_user}@{self.ssh_node}:{remote_generated_file_path}")

    def start_workload(self, workload=None, output=None, detach=True):
        # start fio environment and kill existing fio process
        # executed in detach mode by adding option -d
        workload = workload or self.workload
        self.generate_fio_conf(workload)
        fio_exec_cmd = f"sh {self.fio_script_path}"
        if detach:
            fio_exec_cmd += " -d"
        if output is not None:
            fio_exec_cmd += f" -o {output}"
        logger.info(f"start workload {fio_exec_cmd}")
        exec_remote_cmd(self.ssh_user, self.ssh_node, fio_exec_cmd)
