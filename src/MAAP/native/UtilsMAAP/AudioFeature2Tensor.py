import numpy as np

from MAAP.native.AudioFeature import AudioFeature


class AudioFeature2Tensor:
    """"""

    def __init__(self, audioFeature: AudioFeature):
        """Constructor for AudioFeature2Tensor"""
        self.audioFeature = audioFeature
        self.features_name = list(audioFeature.keys())
        self.output_tensor = None
        self.tensor_elements_buffer = list()

    def translate(self):
        for feature_name in self.features_name:
            tensor_elements = self._convert_feature_to_tensor_elements(
                self.audioFeature[feature_name]
            )
            self.tensor_elements_buffer.append(tensor_elements)

        final_tensor = self._concat_elements_from_buffer()

        return final_tensor

    @staticmethod
    def _convert_constant_to_tensor_elements(constant: float):
        NotImplementedError()

    @staticmethod
    def _convert_1darray_to_tensor_elements(array: np.ndarray):
        NotImplementedError()

    @staticmethod
    def _convert_2darray_to_tensor_element(array: np.ndarray):
        NotImplementedError()

    def _convert_feature_to_tensor_elements(self, feature_value: np.ndarray):
        if isinstance(feature_value, float):
            return self._convert_constant_to_tensor_elements(feature_value)
        if isinstance(feature_value, np.ndarray):
            if feature_value.ndim == 1:
                return self._convert_1darray_to_tensor_elements(feature_value)
            if feature_value.ndim == 2:
                return self._convert_2darray_to_tensor_element(feature_value)

    def _concat_elements_from_buffer(self):
        raise NotImplementedError()


class AudioFeature2Tensor_1D(AudioFeature2Tensor):
    def __init__(self, audioFeature: AudioFeature):
        AudioFeature2Tensor.__init__(self, audioFeature)

    @staticmethod
    def _convert_constant_to_tensor_elements(constant: float):
        return np.array([constant])

    @staticmethod
    def _convert_1darray_to_tensor_elements(array: np.ndarray):
        return array

    @staticmethod
    def _convert_2darray_to_tensor_element(array: np.ndarray):
        return np.concatenate(array)

    def _concat_elements_from_buffer(self):
        return np.concatenate(self.tensor_elements_buffer)


class AudioFeature2Tensor_2D(AudioFeature2Tensor):
    def __init__(self, audioFeature: AudioFeature):
        AudioFeature2Tensor.__init__(self, audioFeature)

    @staticmethod
    def _convert_constant_to_tensor_elements(constant: float):
        return NotImplementedError()

    @staticmethod
    def _convert_1darray_to_tensor_elements(array: np.ndarray):
        return array.reshape(1, array.shape[0])

    @staticmethod
    def _convert_2darray_to_tensor_element(array: np.ndarray):
        return array

    def _concat_elements_from_buffer(self):
        """
        Normally, you desired that first index indexes time. In AudioFeature, if the values is an 2D array, the
        first index indexes the feature order. Thus, we transpose the matrix to change the last index
        (which indexes time) to the first
        :return:
        """
        return np.concatenate(self.tensor_elements_buffer).T


def audio_feature_2_tensor(audioFeature: AudioFeature, ndim: int = 1):
    """

    :param audioFeature:
    :param ndim: defines the dimensionaly of the tensor. Can be for now, 1D or 2D
    :return:
    """

    if ndim == 1:
        return AudioFeature2Tensor_1D(audioFeature).translate()
    if ndim == 2:
        return AudioFeature2Tensor_2D(audioFeature).translate()
    else:
        raise Exception("ndim={} is not allowed".format(ndim))


if __name__ == "__main__":

    from src.MAAP.native.AudioFeatureExtractor import AudioFeatureExtractor

    audio_file_path = "../../../../audio.files/sir_duke_fast.wav"

    extractor = AudioFeatureExtractor()
    extractor.load_audio_file(audio_file_path)

    extractor.config(
        ("mfcc", "zero_cross_rate"),
        output_format="dict_key_per_feature_dim",
        mfcc_func_args={"n_mfcc": 13, "pooling": "mean"},
        zero_cross_rate_func_args={"pooling": "mean"},
    )

    features = extractor.compute_features_by_config()
    tensor = AudioFeature2Tensor(features, ndim=1)

    extractor.config(
        ("mfcc", "zero_cross_rate"),
        output_format="dict_key_per_feature_dim",
        mfcc_func_args={"n_mfcc": 13},
        zero_cross_rate_func_args={},
    )
    features = extractor.compute_features_by_config()
    tensor = AudioFeature2Tensor(features, ndim=1)

    extractor.config(
        ("mfcc", "zero_cross_rate"),
        output_format="dict_key_per_feature",
        mfcc_func_args={"n_mfcc": 13},
        zero_cross_rate_func_args={},
    )
    features = extractor.compute_features_by_config()
    tensor = AudioFeature2Tensor(features, ndim=1)
    tensor = AudioFeature2Tensor(features, ndim=2)

    features = extractor.compute_all_features()
    tensor = AudioFeature2Tensor(features, ndim=2)
    tensor = AudioFeature2Tensor(features, ndim=1)
