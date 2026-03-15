"""NavSysLib package initializer.

Exports core classes and utilities for NMEA sentence handling.
"""

# re-export symbols for convenience
from .NMEASentence import *
from .NMEALog import NMEALog
from .utilities import *
from .Coords import WGS84Coords

__all__ = [
    # NMEASentence classes
    "NMEASentence", "GGASentence", "GLLSentence", "GSASentence", "GSVSentence",
    "RMCSentence", "VTGSentence", "ZDASentence", "NMEALog",
    # utilities
    "safe_int", "safe_float", "dm_to_deg",
    # coordinate helpers
    "WGS84Coords",
]
