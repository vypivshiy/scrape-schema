import logging

__all__ = ["logger"]

logger = logging.getLogger("scrape_schema")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(formatter)

logger.addHandler(stdout_handler)
