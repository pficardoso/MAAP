__all__ = [
    "AudioCutter",
    "AudioFeature",
    "AudioFeatureExtractor",
    "AudioReader",
    "AudioReceiver",
    "AudioSignal",
    "AudioWriter",
    "utils",
    "threads",
]

import sys

from MAAP import threads, utils
from MAAP.AudioCutter import AudioCutter
from MAAP.AudioFeature import AudioFeature
from MAAP.AudioFeatureExtractor import AudioFeatureExtractor
from MAAP.AudioReader import AudioReader
from MAAP.AudioReceiver import AudioReceiver
from MAAP.AudioSignal import AudioSignal
from MAAP.AudioWriter import AudioWriter

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
