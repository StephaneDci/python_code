# -*- coding: utf-8 -*-

import os
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def verify_if_file_exists(filepath: str, expected_size: int = None) -> Tuple[bool, str]:
    if not os.path.isfile(filepath):
        return False, f"FILE: '{filepath}' DOES NOT EXISTS"
    else:
        if expected_size is not None:
            if actual_size := os.path.getsize(filepath) != expected_size:
                return (False, f"FILE SIZE for '{filepath}' IS NOT CORRECT.\n"
                               f"Actual: {actual_size} vs Expected: {expected_size}")
        return True, "FILE OK"

def create_target_directory(directory: str) -> bool:
    if not os.path.exists(directory):
        try:
            logger.debug(f"Creating directory '{directory}'.")
            os.makedirs(directory)
        except Exception as exc:
            logger.exception(f"Error: {exc}")
            raise Exception(f"exception Occurred {exc}")
        else:
            logger.debug("Success!")
            return True
    else:
        logger.debug(f"Directory already exists: '{directory}'.")
        return False