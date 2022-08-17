"""EduuRobot core package."""
# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from subprocess import run

__version__ = "2.1.0"
__version_code__ = (
    run(["git", "rev-list", "--count", "HEAD"], capture_output=True)
    .stdout.decode()
    .strip()
    or "0"
)
