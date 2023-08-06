# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os

import setuptools

BASE_DIR = os.path.dirname(__file__)
VERSION_FILENAME = os.path.join(BASE_DIR, "src", "azure_monitor", "version.py")
PACKAGE_INFO = {}
with open(VERSION_FILENAME) as f:
    exec(f.read(), PACKAGE_INFO)

setuptools.setup(version=PACKAGE_INFO["__version__"])
