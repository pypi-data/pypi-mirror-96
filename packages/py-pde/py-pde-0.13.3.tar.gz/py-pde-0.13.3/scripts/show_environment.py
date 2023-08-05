#!/usr/bin/env python3
"""
This script shows important information about the current python environment and the
associated installed packages. This information can be helpful in understanding issues
that occur with the package
"""

import sys
from collections import OrderedDict
from pathlib import Path

PACKAGE_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PACKAGE_PATH))

from pde import environment

env = environment(OrderedDict)

for category, data in env.items():
    if hasattr(data, "items"):
        print(f"\n{category}:")
        for key, value in data.items():
            print(f"    {key}: {value}")
    else:
        data_formatted = data.replace("\n", "\n    ")
        print(f"{category}: {data_formatted}")
