import sounddevice as sd
import librosa
import numpy as np
import matplotlib.pyplot as plt
import math

class AudioSignal():
    """"""

    def __init__(self, y, sample_rate):
        """Constructor for AudioSignal"""
        ## check if AudioSignal is a np.array
        if not isinstance(y, np.ndarray):
            raise Exception("y value must be a numpy.ndarray data type")

        self.y = y
        self.sr = sample_rate
        self.t = [1/self.sr * i for i in np.arange(0,len(self.y),1)]
        self.duration = librosa.get_duration(self.y, self.sr)


    def play_audio(self):
        sd.play(self.y, self.sr, blocking=True)

    def get_duration(self):
        return self.duration


    def plot_signal(self):
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
    t = np.arange(0,100,1)
    y = np.sin(t * np.pi/20)
    audioSignal = AudioSignal(y, 2000)
    audioSignal.plot_signal()

