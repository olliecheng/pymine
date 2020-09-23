#!/usr/bin/env python3
#
#   Handles stdout logging.
#
#  A part of denosawr/pymine

import colorlog
import logging

from typing import Optional

DEFAULT_LEVEL = "INFO"


# TODO: change logging level via command line


def getLogger(name: Optional[str] = None) -> logging.Logger:
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s:%(name)s:%(message)s",
            log_colors={
                "DEBUG": "white",
                "INFO": "cyan",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    logger = colorlog.getLogger(name)
    logger.addHandler(handler)

    logger.setLevel(DEFAULT_LEVEL)
    return logger
