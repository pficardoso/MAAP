import sounddevice as sd
import librosa
import numpy as np
import matplotlib.pyplot as plt
import datetime


class AudioSignal():
    """"""

    def __init__(self, y, sample_rate):
        """Constructor for AudioSignal"""

        self._check_initial_parameters(y, sample_rate)

        self.y = y
        self.sr = sample_rate
        self.duration = librosa.get_duration(self.y, self.sr)


    def __repr__(self):
        ## print class
        class_name = type(self).__name__
        duration = datetime.timedelta(seconds=self.duration)
        return '{}(sample_rate = {} Hz; duration = {};)'.format(class_name, self.sr, duration,)

    def __add__(self, audio_signal_ins):
        if not isinstance(audio_signal_ins, AudioSignal):
            raise Exception("Audio_signal_ins should be an instance of AudioSignal")
        if self.sr != audio_signal_ins.sr:
            raise Exception("SampleRate of both signals should be the same")

        new_y = np.concatenate((self.y, audio_signal_ins.y))
        return AudioSignal(new_y, self.sr)

    def get_data(self):
        return self.y

    def get_sample_rate(self):
        return self.sr

    def get_duration(self):
        return self.duration

    @staticmethod
    def _check_initial_parameters( y, sample_rate ):
        # y must by a np.ndarray with 1-dim
        if (not isinstance(y, np.ndarray) ) or ( y.ndim != 1):
            raise Exception("y value must be a numpy.ndarray data type with 1-dimension")

    def play_audio(self):
        sd.play(self.y.transpose(), self.sr, blocking=True)

    def plot_signal(self, channel=0):

        self.t = [1 / self.sr * i for i in np.arange(0, len(self.y), 1)]
        fig, ax = plt.subplots(1, 1)
        step_seconds = 1/self.sr
        t = [1/self.sr * i for i in np.arange(0,len(self.y),1)]
        ax.set_xlabel("Time (s)")
        ax.plot(t, self.y)
        ax.grid(True)
        ax.set_ylim(self.y.min(), self.y.max())
        fig.tight_layout()
        plt.show()


if __name__ == "__main__":

    duration = 2
    sample_rate = 40000
    nr_frames = duration*sample_rate
    t = np.arange(0,nr_frames,1)
    y = np.sin(t * np.pi/20000)
    audioSignal = AudioSignal(y, sample_rate)
    print(repr(audioSignal))
    audioSignal.plot_signal()


