from src.MAAP.native.AudioSignal import AudioSignal
from src.MAAP.native.AudioWriter import AudioWriter

import numpy as np
import os
import sounddevice as sd
import soundfile as sf
import re

class AudioReader():
    """"""

    def __init__(self, file_path : str):
        """Constructor for """
        self._file_path = None
        self.set_file_path(file_path)

    @staticmethod
    def valid_extension(file_path : str):
        return bool(re.match(".*\.wav$", os.path.basename(file_path)))

    def set_file_path(self, file_path : str):
        if self.valid_extension(file_path):
            self._file_path = file_path
        else:
            Exception("The file {} must be an .wav file".format(file_path))

    def read(self, file_path=None):

        if file_path:
            self.set_file_path(file_path)

        print(self._file_path)
        try:
            y, sr = sf.read(self._file_path)
        except Exception as e:
            raise Exception("{}".format(e))

        return AudioSignal(y, sr)

if __name__ == "__main__":

    duration = 2
    sample_rate = 44100
    nr_frames = duration*sample_rate
    t = np.arange(0,nr_frames,1)
    y = np.sin(t * np.pi/20000)
    audioSignal = AudioSignal(y, sample_rate)

    writer = AudioWriter("/tmp/", "1.wav", audioSignal).write()
    audioSignal = AudioReader(os.path.join("/tmp/", "1.wav")).read()
    audioSignal.plot_signal()
