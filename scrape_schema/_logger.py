import logging

import colorlog

__all__ = ["_logger"]

handler = colorlog.StreamHandler()
_formatter = colorlog.ColoredFormatter(
    fmt="%(log_color)s %(asctime)s [%(levelname)-8s] %(name)s: %(message)s'"
)

handler.setFormatter(_formatter)

_logger = logging.getLogger("scrape_schema")
_logger.addHandler(handler)
_logger.setLevel(logging.DEBUG)
