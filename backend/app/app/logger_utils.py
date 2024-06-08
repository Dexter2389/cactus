import logging
import sys


def setup_logging(log_level=logging.INFO):
    log_format = "[%(asctime)s] [%(process)d] [%(levelname)s] [%(module)s:%(lineno)d (%(funcName)s)] %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
