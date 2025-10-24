#!/usr/bin/env python3
# logging.py: logging configuration

import logging 
import sys
import os
from pathlib import Path
from typing import Optional

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    log_level = level or 'INFO'  # Default to INFO if no level provided
    logger.setLevel(getattr(logging, log_level.upper()))

    formatter = logging.Formatter(
        '{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
            datefmt='%Y-%m-%dT%H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger