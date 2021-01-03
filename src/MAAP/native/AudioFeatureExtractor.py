import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import configparser
from src.MAAP.native.AudioSignal import AudioSignal
from src.MAAP.native.AudioReader import AudioReader


python_list_format_pattern = "\[((\s)*([a-zA-z1-9])+(\s)*(\,)?(\s)*)+\]"

DEFAULT_OUTPUT_FORMAT = 'dict_key_per_feature'
AVAILABLE_OUTPUT_FORMAT = ['dict_key_per_feature', 'dict_key_per_feature_category']
AVAILABLE_KEYS_MAIN_SECTION_CONFIG = ["features", "outputformat"] # module config parser is case insensitive

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
        self._config_features = None
        self._config_output_format = None
        self._config_features_kwarg_dict = None
        self._configured_by_file = False

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

    def config_by_file(self, file_path):

        conf = configparser.ConfigParser()
        if not os.path.isfile(file_path):
            raise Exception("{} does not exist or is not a file".format(file_path))

        conf.read(file_path)

        # check the values in the section main
        if not set(conf["Main"]).issubset(set(AVAILABLE_KEYS_MAIN_SECTION_CONFIG)):
            raise Exception(" Features with name(s) '{}' do not exist"
                            .format(set(conf["Main"]).difference(set(AVAILABLE_KEYS_MAIN_SECTION_CONFIG))))

        # get the features in main
        features_value = conf['Main']['Features']
        if re.match(python_list_format_pattern, features_value):
            ##it is a string with a list format
            features_list = re.sub("[\[\]\s]","",features_value).split(",")
            ## Check if all features_list are available
            if not set(features_list).issubset(set(features_dict)):
                raise Exception(" Features with name(s) '{}' do not exist"
                                .format(set(features_list).difference(set(features_dict))))
        elif features_value.strip() == "all":
            ## get all the features name
            features_list = list(features_dict.keys())
        else:
            raise Exception("Value of Features must has python list format or value 'all'")

        ##sort the list of features
        features_list = sorted(features_list)

        # get the output_format in main
        output_format = DEFAULT_OUTPUT_FORMAT
        if "OutputFormat" in conf["Main"]:
            output_format = conf["Main"]["OutputFormat"]
            if output_format not in AVAILABLE_OUTPUT_FORMAT:
                raise Exception("OutputFormat '{}' not available. Allowed values are '{}'".format(output_format, AVAILABLE_OUTPUT_FORMAT))

        ##define the section_names for each feature
        feature_section_names = [name + "_func_args" for name in features_list]

        features_kwarg_dict = {}
        for i in range(0, len(features_list)):
            section_name = feature_section_names[i]
            if not section_name in conf:
                features_kwarg_dict[features_list[i]] = {}
                continue
            features_kwarg_dict[features_list[i]] = dict(conf[section_name])

        self._config_features = features_list
        self._config_output_format = output_format
        self._config_features_kwarg_dict = features_kwarg_dict
        self._configured_by_file = True

    def reset_config(self):
        self._config_features = None
        self._config_output_format = None
        self._config_features_kwarg_dict = None
        self._configured_by_file = False

    def compute_features_by_config(self):
        if not self._configured_by_file:
            raise Exception("FeatureExtractor instance is not configured")

        # get the list with the functions to be runn
        features_func_list = [features_dict[feature_name] for feature_name in self._config_features]
        features_values_dict = dict()
        for i in range(0, len(self._config_features)):
            feature_name = self._config_features[i]
            features_values_dict[feature_name] = features_func_list[i](self, **self._config_features_kwarg_dict[feature_name])

        return features_values_dict

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
        roll_percent = float(roll_percent)
        rol = librosa.feature.spectral_rolloff(self.y, self.sample_rate, roll_percent=roll_percent)[0]
        return rol

    @audio_feature("mfcc")
    def compute_feature_mfcc(self, n_mfcc=20):
        ## from config files, values are fetched as string. This n_mfcc must be converted to int
        n_mfcc = int(n_mfcc)
        mfccs = librosa.feature.mfcc(self.y, self.sample_rate, n_mfcc=n_mfcc)
        return mfccs

    @audio_feature("rms")
    def compute_feature_rms(self):
        return librosa.feature.rms(self.y)[0]

if __name__=="__main__":

    audio_file_path = "../../../audio.files/sir_duke_fast.wav"
    config_file_path = "/workspace/tmp/test.ini"
    extractor = AudioFeatureExtractor()
    extractor.load_audio_file(audio_file_path)
    extractor.compute_spectrogram(True)

    extractor.config_by_file(config_file_path)
    extractor.compute_features_by_config()