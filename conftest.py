"""Global pytest configuration for test suite."""

import warnings

warnings.filterwarnings(
    "ignore",
    message=r"builtin type SwigPy.*has no __module__ attribute",
    category=DeprecationWarning,
)
