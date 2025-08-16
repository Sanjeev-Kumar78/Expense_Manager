"""Backend package initializer.

This module exposes the main subpackages for convenient imports.
"""
from . import routes
from . import services
from . import utils

__all__ = ["routes", "services", "utils"]
