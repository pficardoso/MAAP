import datetime

import librosa
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd


class AudioSignal:
    """"""

    def __init__(self, y, sample_rate):
        """Constructor for AudioSignal"""

        self._check_initial_parameters(y, sample_rate)

        self.y = y
        self.sr = sample_rate
        self.duration = librosa.get_duration(self.y, self.sr)

    def __repr__(self):
        class_name = type(self).__name__
        duration = datetime.timedelta(seconds=self.duration)
        return "{}(sample_rate = {} Hz; duration = {};)".format(
            class_name,
            self.sr,
            duration,
        )

    def __add__(self, audio_signals):
        # audio_signal is an instance of AudioSignala
        if isinstance(audio_signals, AudioSignal):
            new_y = np.concatenate((self.y, audio_signals.y))
            if self.sr != audio_signals.sr:
                raise Exception(
                    "SampleRate of signals should be the same. {} {}".format(
                        self, audio_signals
                    )
                )

        # audio_signal is a list of audio_signal
        elif all(
            isinstance(audio_signal, AudioSignal) for audio_signal in audio_signals
        ):
            audios_to_concat = (
                self.y,
                *[audio_signal.y for audio_signal in audio_signals],
            )
            new_y = np.concatenate(audios_to_concat)
            for audio_signal in audio_signals:
                if self.sr != audio_signal.sr:
                    raise Exception(
                        "SampleRate of signals should be the same. {} {}".format(
                            self, audio_signal
                        )
                    )
        else:
            raise Exception(
                "audio_signals must be an instance of AudioSignal or a list of AudioSignals"
            )

        return AudioSignal(new_y, self.sr)

    def get_data(self):
        return self.y

    def get_sample_rate(self):
        return self.sr

    def get_duration(self):
        """

        :return: in seconds
        """
        return self.duration

    def get_timestamps_samples(self):
        return [1 / self.sr * i for i in np.arange(0, len(self.y), 1)]

    @staticmethod
    def _check_initial_parameters(y, sample_rate):
        # y must by a np.ndarray with 1-dim
        if (not isinstance(y, np.ndarray)) or (y.ndim != 1):
            raise Exception(
                "y value must be a numpy.ndarray data type with 1-dimension"
            )

    def play_audio(self):
        sd.play(self.y.transpose(), self.sr, blocking=True)

    def plot_signal(self, channel=0, ax=None):

        if ax is None:
            ax = plt.gca()

        self.t = [1 / self.sr * i for i in np.arange(0, len(self.y), 1)]
        t = self.get_timestamps_samples()
        ax.set_xlabel("Time (s)")
        ax.plot(t, self.y)
        ax.grid(True)
        ax.set_ylim(self.y.min(), self.y.max())

        return ax


if __name__ == "__main__":

    duration = 2
    sample_rate = 40000
    nr_frames = duration * sample_rate
    t = np.arange(0, nr_frames, 1)
    y = np.sin(t * np.pi / 20000)
    audioSignal = AudioSignal(y, sample_rate)
    print(repr(audioSignal))
    audioSignal.plot_signal()
