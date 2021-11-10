__all__ = [
    "AudioCutter",
    "AudioFeature",
    "AudioFeatureExtractor",
    "AudioReader",
    "AudioReceiver",
    "AudioSignal",
    "AudioWriter",
    "utils",
]

import sys

# import MAAP.utils
# from MAAP.utils import func1 func2
from MAAP.native import utils
from MAAP.native.AudioCutter import AudioCutter
from MAAP.native.AudioFeature import AudioFeature
from MAAP.native.AudioFeatureExtractor import AudioFeatureExtractor
from MAAP.native.AudioReader import AudioReader
from MAAP.native.AudioReceiver import AudioReceiver
from MAAP.native.AudioSignal import AudioSignal
from MAAP.native.AudioWriter import AudioWriter

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
