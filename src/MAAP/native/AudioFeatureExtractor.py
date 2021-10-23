import librosa.display
import matplotlib.pyplot as plt
import numpy as np

from MAAP.native.AudioFeature import AudioFeature
from MAAP.native.AudioReader import AudioReader
from MAAP.native.AudioSignal import AudioSignal

DEFAULT_OUTPUT_FORMAT = "dict_key_per_feature"
AVAILABLE_OUTPUT_FORMAT = ["dict_key_per_feature", "dict_key_per_feature_dim"]
AVAILABLE_KEYS_MAIN_SECTION_CONFIG = [
    "features",
    "output_format",
]  # module config parser is case insensitive
N_MFCC_DEFAULT = 20

compute_feature_functions_dict = dict()


def audio_feature(feature_name):
    def decorate(compute_feature_function):
        compute_feature_functions_dict[feature_name] = compute_feature_function
        return compute_feature_function

    return decorate


class AudioFeatureExtractor:
    """"""

    def __init__(
        self,
    ):
        """Constructor for AudioFeatureExtractor"""
        self.audioSignal = None
        self.audio_file_path = None
        self._config_features = None
        self._config_audio_feature_output = AudioFeature()
        self._config_features_functions_kwarg_dict = None
        self._configured = False

    def load_audio_file(self, file_path):

        self.audioSignal = AudioReader(file_path).read()
        self.audio_file_path = file_path
        self.y = self.audioSignal.get_data()
        self.sample_rate = self.audioSignal.get_sample_rate()

    def load_audio_signal(self, audioSignal: AudioSignal):
        # check if it is an AudioSignal
        self.audio_file_path = None
        self.audioSignal = audioSignal
        self.y = self.audioSignal.get_data()
        self.sample_rate = self.audioSignal.get_sample_rate()

    def config(self, features_to_use, output_format=DEFAULT_OUTPUT_FORMAT, **kwargs):
        self.reset_config()
        """
        check features_to_use. Must have the str "all" to select all the features,
        or have a sequence with the features name to use
        """
        global compute_feature_functions_dict
        if isinstance(features_to_use, str):
            if features_to_use != "all":
                raise Exception(
                    'if features_to_use is a str datatype, its value must be a "all"'
                )
            else:
                features_to_use = set(compute_feature_functions_dict.keys())
        elif isinstance(features_to_use, (list, tuple, set)):
            features_to_use = set(features_to_use)  # convert to list
            wrong_features = [
                feature_name
                for feature_name in features_to_use
                if feature_name not in compute_feature_functions_dict
            ]
            if len(wrong_features) != 0:
                raise Exception(
                    "features {} do not exist. Allowed features are {}".format(
                        wrong_features, list(compute_feature_functions_dict.keys())
                    )
                )
        else:
            raise Exception(
                "features_to_use should be a dict, tuple, set datatype, "
                'or the str "all" to select all features'
            )

        # check output format
        if output_format not in AVAILABLE_OUTPUT_FORMAT:
            raise Exception(
                "output_format '{}' not available. Allowed values are '{}'".format(
                    output_format, AVAILABLE_OUTPUT_FORMAT
                )
            )

        # check if kwargs contains all function arguments for each feature function, and if their values type is a dict.
        required_keys_from_kwargs = [
            "{}_func_args".format(feature_name) for feature_name in features_to_use
        ]
        missing_keys_from_kwargs = [
            key for key in required_keys_from_kwargs if key not in kwargs.keys()
        ]
        if len(missing_keys_from_kwargs) != 0:
            raise Exception(
                " Key args {} were not passed to the function".format(
                    missing_keys_from_kwargs
                )
            )
        not_dict = [
            key
            for key in required_keys_from_kwargs
            if not isinstance(kwargs[key], dict)
        ]
        if len(not_dict) != 0:
            raise Exception(
                " Keys of {} kwargs must be a dictionary (can be an empty dictionary)".format(
                    not_dict
                )
            )

        # The self._config_features must be sorted
        self._config_features = sorted(features_to_use)
        self._config_output_format = output_format
        self._config_features_functions_kwarg_dict = {
            feature_name: kwargs["{}_func_args".format(feature_name)]
            for feature_name in features_to_use
        }
        self._configured = True
        self._prepare_output_dict_format()

    def reset_config(self):
        self._config_features = None
        self._config_output_format = None
        self._config_features_functions_kwarg_dict = None
        self._configured = False

        # also re-instance AudioFeature object, to forget the keys previously inserted
        self._config_audio_feature_output = AudioFeature()

    def is_configured_by_file(self):
        return self._configured

    def _prepare_output_dict_format(self):
        self._config_output_feature_fetch_direct = self._config_features.copy()
        self._config_output_feature_fetch_iterate = list()

        if self._config_output_format == "dict_key_per_feature":
            [
                self._config_audio_feature_output.setdefault(feature_name, None)
                for feature_name in self._config_features
            ]
            return

        if self._config_output_format == "dict_key_per_feature_dim":
            config_features = list(self._config_features.copy())
            if "mfcc" in self._config_features:
                self._config_output_feature_fetch_direct.remove("mfcc")
                config_features.remove("mfcc")

                if (
                    "n_mfcc"
                    in self._config_features_functions_kwarg_dict["mfcc"].keys()
                ):
                    n_dim = self._config_features_functions_kwarg_dict["mfcc"]["n_mfcc"]
                else:
                    n_dim = N_MFCC_DEFAULT

                self._config_output_feature_fetch_iterate.append(("mfcc", 1, n_dim + 1))
                for i in range(1, n_dim + 1):
                    config_features.append("mfcc_" + str(i))

            # sort the keys
            [
                self._config_audio_feature_output.setdefault(feature_name, None)
                for feature_name in sorted(config_features)
            ]
            return

    def compute_features_by_config(self):
        global compute_feature_functions_dict
        if not self._configured:
            raise Exception("FeatureExtractor instance is not configured")

        # get the list with the functions to be run

        features_values_dict = dict()
        for feature_name in self._config_features:
            feature_kwarg_dict = self._config_features_functions_kwarg_dict[
                feature_name
            ]
            features_values_dict[feature_name] = compute_feature_functions_dict[
                feature_name
            ](self, **feature_kwarg_dict)

        for feature_name in self._config_output_feature_fetch_direct:
            self._config_audio_feature_output[feature_name] = features_values_dict[
                feature_name
            ]

        for feature_name, start_i, final_i in self._config_output_feature_fetch_iterate:
            i = 0
            for j in range(start_i, final_i):
                self._config_audio_feature_output[
                    "{}_{}".format(feature_name, j)
                ] = features_values_dict[feature_name][i]
                i += 1

        return self._config_audio_feature_output

    def compute_all_features(self):
        audio_feature = AudioFeature()
        features = compute_feature_functions_dict.keys()
        for feature_name in sorted(features):
            audio_feature[feature_name] = compute_feature_functions_dict[feature_name](
                self
            )
        return audio_feature

    @staticmethod
    def _make_poling_array(array: np.array, pooling_strategy=None):
        if not pooling_strategy:
            return array
        if pooling_strategy == "mean":
            return array.mean()
        if pooling_strategy == "max":
            return array.max()
        if pooling_strategy == "sum":
            return array.sum()

        raise Exception("Pooling strategy '{}' is not valid".format(pooling_strategy))

    @audio_feature("spectrogram_magnitude")
    def compute_spectrogram_magnitude(
        self, return_in_db=True, plot=False, pooling=None
    ):
        # And compute the spectrogram magnitude and phase
        S_full, _ = librosa.magphase(librosa.stft(self.y))

        if plot:
            # Plot the spectrum
            fig, ax = plt.subplots()
            img = librosa.display.specshow(
                librosa.amplitude_to_db(S_full, ref=np.max),
                y_axis="log",
                x_axis="time",
                sr=self.sample_rate,
                ax=ax,
            )
            fig.colorbar(img, ax=ax)
            plt.show()

        if return_in_db:
            return librosa.amplitude_to_db(S_full)
        else:
            return S_full

    @audio_feature("zero_cross_rate")
    def compute_feature_zero_cross_rate(self, pooling=None):
        zcr = librosa.feature.zero_crossing_rate(self.y)[0]
        return self._make_poling_array(zcr, pooling)

    @audio_feature("spectral_centroid")
    def compute_feature_spectral_centroid(self, pooling=None):
        ctr = librosa.feature.spectral_centroid(self.y)[0]
        return self._make_poling_array(ctr, pooling)

    @audio_feature("spectral_rolloff")
    def compute_feature_spectral_rolloff(self, roll_percent=0.85, pooling=None):
        roll_percent = float(roll_percent)
        rol = librosa.feature.spectral_rolloff(
            self.y, self.sample_rate, roll_percent=roll_percent
        )[0]
        return self._make_poling_array(rol, pooling)

    @audio_feature("mfcc")
    def compute_feature_mfcc(self, n_mfcc=N_MFCC_DEFAULT, pooling=None):
        # from config files, values are fetched as string. This n_mfcc must be converted to int
        n_mfcc = int(n_mfcc)
        mfccs = librosa.feature.mfcc(self.y, self.sample_rate, n_mfcc=n_mfcc)
        if pooling is not None:
            mfccs = np.array(
                [
                    self._make_poling_array(mfcc_i_array, pooling)
                    for mfcc_i_array in mfccs
                ]
            )
        return mfccs

    @audio_feature("rms")
    def compute_feature_rms(self):
        return librosa.feature.rms(self.y)[0]


if __name__ == "__main__":

    audio_file_path = "../../../audio.files/sir_duke_fast.wav"
    config_file_path = "/workspace/tmp/test.ini"
    extractor = AudioFeatureExtractor()
    extractor.load_audio_file(audio_file_path)

    extractor.config(
        ("mfcc", "zero_cross_rate"),
        output_format="dict_key_per_feature_dim",
        mfcc_func_args={"n_mfcc": 13, "pooling": "mean"},
        zero_cross_rate_func_args={},
    )

    features = extractor.compute_features_by_config()
    features

    extractor.config(
        ("mfcc", "zero_cross_rate"),
        output_format="dict_key_per_feature",
        mfcc_func_args={"n_mfcc": 13, "pooling": "mean"},
        zero_cross_rate_func_args={},
    )
    features = extractor.compute_features_by_config()
    features

    features = extractor.compute_all_features()
    features
