from collections import OrderedDict


class AudioFeature(OrderedDict):
    """
    Basically is a dictionar whose keys will be the name of the feature, and the value will be the features values.

    The AudioFeature is an OrderedDict, this is, remembers the order in which the elements have been inserted.
    This is useful for MAAP.AudioFeatureExtractor. AudiFeatureExtractor analyses a signal and computes its feactures,
    and returns them as output, using this class instance. It is desired that, for different sets of features selected
    in AudioFeatureExtractor, the organization of the output is well organized, i.e, their items are sorted. As example,
    a sort strategy could be sort the keys alphabetically. The OrderedDict inheritance allows AudioFeatureExtractor
    to control how features are organized in AudioFeature instance. For that, AudiFeatureExtractor will need to
    insert the features with the desired order, in order to AudioFeature remember it.


    TOIMPROVE: Currently, the AudioFeature allows its good organization because inherits a OrderedDict. Its organization
         depends how their keys are inserted. For now, this process is managed by how calls AudioFeature instance.
         In the future, should be AudioFeature to manage that internally

    """

    def __init__(self):
        """Constructor for AudioFeature"""
        super().__init__()

    """
    Setters/Loaders
    """

    """
    Getters
    """

    def get_features(self, features=iter, n_mfcc=13):
        """
        Import return features with the correct order.
        """
        output_dict = dict()
        for feature_name, feature_value in self.items():
            if feature_name in features:
                if feature_name == "mfcc":
                    output_dict[feature_name] = feature_value[0:n_mfcc]
                else:
                    output_dict[feature_name] = feature_value
        return output_dict

    """
    Workers
    """

    """
    Logic methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """


if __name__ == "__main__":

    from src.MAAP.native.AudioFeatureExtractor import AudioFeatureExtractor

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
    print(features.get_features(("mfcc")))
