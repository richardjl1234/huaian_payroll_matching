#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Configuration file for the quota processing system
# Get the absolute path of the current directory
CURRENT_DIR = Path(__file__).parent

# Database path - absolute path
DATABASE_PATH = str(CURRENT_DIR.parent / "payroll_database.db")

# Common directory path - absolute path
COMMON = str(CURRENT_DIR.parent / "common")

# Translation dictionary path - absolute path
TRANSLATION_DICT = str(CURRENT_DIR.parent / "common" / "translation_dict.pkl")
