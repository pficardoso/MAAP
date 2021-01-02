import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from src.MAAP.native.AudioSignal import AudioSignal
from src.MAAP.native.AudioReader import AudioReader

features_dict = dict()


def audio_feature(feature_name):
    def decorate(compute_feature_function):
        features_dict[feature_name] = compute_feature_function
        return compute_feature_function
    return decorate


class AudioFeatureExtractor():
    """"""
    features_dict = dict()

    def __init__(self,):
        """Constructor for AudioFeatureExtractor"""
        self.audioSignal = None
        self.audio_file_path = None
    ##def __repr__(self):
    ##    pass

    def load_audio_file(self, file_path):

        self.audioSignal = AudioReader(file_path).read()
        self.audio_file_path = file_path
        self.y  = self.audioSignal.get_data()
        self.sample_rate = self.audioSignal.get_sample_rate()

    def load_audio_signal(self, audioSignal: AudioSignal):
        ## check if it is an AudioSignal
        self.audio_file_path = None
        self.audioSignal     = audioSignal
        self.y = self.audioSignal.get_data()
        self.sample_rate = self.audioSignal.get_sample_rate()


    def compute_all_features(self):
        return {feature_name: feature_function(self) for feature_name, feature_function in features_dict.items()}

    @audio_feature("spectrogram")
    def compute_spectrogram(self, return_in_db=True, plot=False):
        # And compute the spectrogram magnitude and phase
        S_full, phase = librosa.magphase(librosa.stft(self.y))

        if plot:
            # Plot the spectrum
            fig, ax = plt.subplots()
            img = librosa.display.specshow(librosa.amplitude_to_db(S_full, ref=np.max),
                                           y_axis='log', x_axis='time', sr=self.sample_rate , ax=ax)
            fig.colorbar(img, ax=ax)
            plt.show()

        if return_in_db:
            return librosa.amplitude_to_db(S_full), phase
        else:
            return S_full, phase

    @audio_feature("zero_cross_rate")
    def compute_feature_zero_cross_rate(self):
        zcr = librosa.feature.zero_crossing_rate(self.y)[0]
        return zcr

    @audio_feature("spectral_centroid")
    def compute_feature_spectral_centroid(self):
        ctr = librosa.feature.spectral_centroid(self.y)[0]
        return ctr

    @audio_feature("spectral_rolloff")
    def compute_feature_spectral_rolloff(self, roll_percent=0.85):
        rol = librosa.feature.spectral_rolloff(self.y, self.sample_rate, roll_percent=roll_percent)[0]
        return rol

    @audio_feature("mfcc")
    def compute_feature_mfcc(self, n_mfcc=20):
        mfccs = librosa.feature.mfcc(self.y, self.sample_rate, n_mfcc=n_mfcc)
        return mfccs

    @audio_feature("rms")
    def compute_feature_rms(self):
        return librosa.feature.rms(self.y)[0]

if __name__=="__main__":

    audio_file_path = "../../../audio.files/sir_duke_fast.wav"
    print(features_dict)
    extractor = AudioFeatureExtractor()
    extractor.load_audio_file(audio_file_path)
    extractor.compute_spectrogram(True)
    print("Computing features")
    print(extractor.compute_all_features())
