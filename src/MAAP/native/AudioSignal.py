import sounddevice as sd
import librosa
import numpy as np

class AudioSignal():
    """"""

    def __init__(self, y, sample_rate):
        """Constructor for AudioSignal"""
        ## check if AudioSignal is a np.array
        if not isinstance(y, np.ndarray):
            raise Exception("y value must be a numpy.ndarray data type")

        self.y = y
        self.sr = sample_rate
        self.duration = librosa.get_duration(self.y, self.sr)


    def play_audio(self):
        sd.play(self.y, self.sr, blocking=True)

    def get_duration(self):
        return self.duration

