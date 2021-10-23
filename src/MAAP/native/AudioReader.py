import os
import re

import numpy as np
import soundfile as sf

from MAAP.native.AudioSignal import AudioSignal
from MAAP.native.AudioWriter import AudioWriter


class AudioReader:
    """"""

    def __init__(self, file_paths=None):
        """Constructor for """
        if file_paths is None:
            pass
        else:
            self.set_file_path(file_paths)

    @staticmethod
    def valid_extension(file_path: str):
        return bool(re.match(".*\.wav$", os.path.basename(file_path)))

    def set_file_path(self, file_paths):

        self._file_path = list()

        if isinstance(file_paths, str):
            file_paths = [file_paths]
        elif isinstance(file_paths, tuple):
            file_paths = list(file_paths)

        for file_path in file_paths:
            if self.valid_extension(file_path):
                self._file_path.append(file_path)
            else:
                Exception("The file {} must be an .wav file".format(file_path))

    def read(self, file_paths=None):

        if file_paths:
            self.set_file_path(file_paths)

        list_y = list()
        list_sr = list()
        for file_path in self._file_path:
            try:
                y, sr = sf.read(file_path)
                list_y.append(y)
                list_sr.append(sr)
            except Exception as e:
                raise Exception("{}".format(e))

        set_sr = set(list_sr)
        if len(set_sr) > 1:
            raise Exception(
                "The sample rates of audios are differents. Audio paths {}".format(
                    self._file_path
                )
            )

        return AudioSignal(np.concatenate(list_y), list_sr[0])


if __name__ == "__main__":

    duration = 2
    sample_rate = 44100
    nr_frames = duration * sample_rate
    t = np.arange(0, nr_frames, 1)
    y = np.sin(t * np.pi / 20000)
    audioSignal = AudioSignal(y, sample_rate)

    writer = AudioWriter("/tmp/", "1.wav", audioSignal).write()
    audioSignal = AudioReader(os.path.join("/tmp/", "1.wav")).read()
    audioSignal.plot_signal()
