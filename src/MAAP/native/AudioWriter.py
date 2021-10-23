import os

import numpy as np
import soundfile as sf

from MAAP.native.AudioSignal import AudioSignal


class AudioWriter:
    """"""

    def __init__(self, dir_path, file_name, audio_signal):
        """Constructor for """

        # checks if audio signal
        if not isinstance(audio_signal, AudioSignal):
            raise Exception(
                "audio_signal must be an instance of class {}".format(
                    AudioSignal.__name__
                )
            )

        self._dir_path = dir_path
        # checks if directory_path already exists
        if not os.path.isdir(self._dir_path):
            raise Exception(
                "Directory '{}' does not exist".format(os.path.abspath(self._dir_path))
            )

        self._audio_signal = audio_signal
        self._file_name = file_name
        self._final_path_name = os.path.join(self._dir_path, (self._file_name))

    def write(self):
        sf.write(
            self._final_path_name,
            self._audio_signal.get_data(),
            int(self._audio_signal.get_sample_rate()),
        )


if __name__ == "__main__":

    duration = 2
    sample_rate = 40000
    nr_frames = duration * sample_rate
    t = np.arange(0, nr_frames, 1)
    y = np.sin(t * np.pi / 20000)
    audioSignal = AudioSignal(y, sample_rate)
    print(repr(audioSignal))
    audioSignal.plot_signal()

    writer = AudioWriter("/tmp/", "1.wav", audioSignal).write()
