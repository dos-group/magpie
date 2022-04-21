import logging
from unittest import TestCase

from magpie.utils import magpie_logging


class Test(TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger(__name__)
    def test_init(self):
        magpie_logging.init("/Users/diskun/Work/Workspace/Python/Magpie/magpie/log/test")
        # magpie_logging.init()
        logger = logging.getLogger(__name__)
        logger.warning("warning")
        logger.debug("debug")
        logger.info("info")
        logging.getLogger("root").info("hi")
        self.logger.info("self.logger")

    def test_core_info_logger(self):
        magpie_logging.init("/Users/diskun/Work/Workspace/Python/Magpie/magpie/log/test")
        logger = logging.getLogger("core_info")
        logger.setLevel(logging.INFO)
        logger.info("hi")
