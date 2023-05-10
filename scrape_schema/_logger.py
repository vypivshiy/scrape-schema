import logging

import colorama

__all__ = ["logger"]


colorama.init()


LEVEL_COLORS = {
    "DEBUG": colorama.Style.BRIGHT + colorama.Fore.BLUE,
    "INFO": colorama.Style.BRIGHT + colorama.Fore.GREEN,
    "WARNING": colorama.Fore.YELLOW,
    "ERROR": colorama.Fore.RED,
    "CRITICAL": colorama.Style.BRIGHT + colorama.Fore.RED,
}


class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = LEVEL_COLORS.get(record.levelname, "")
        msg = super().format(record)
        msg = f"{color}{msg}{colorama.Fore.RESET}"
        return msg


class Message:
    def __init__(self, fmt, args):
        self.fmt = fmt
        self.args = args

    def __str__(self):
        return self.fmt.format(*self.args)


class StyleAdapter(logging.LoggerAdapter):
    def __init__(self, logger_, extra=None):
        super().__init__(logger_, extra or {})

    def log(self, level, msg, /, *args, **kwargs):
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger._log(level, Message(msg, args), (), **kwargs)


logger = logging.getLogger("scrape_schema")  # type: ignore
logger.setLevel(logging.DEBUG)
formatter = ColorFormatter(fmt="{asctime} [{levelname}] {message}", style="{")
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
logger = StyleAdapter(logger)  # type: ignore
