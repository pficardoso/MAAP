import queue
import threading

from MAAP.AudioFeatureExtractor import AudioFeatureExtractor


class AudioFeatureExtractorThread(threading.Thread):
    """"""

    def __init__(self, segments_queue: queue.Queue, print_features=False):
        """Constructor for FeatureExtractorQueue"""
        super(AudioFeatureExtractorThread, self).__init__()
        self._featExtractor = AudioFeatureExtractor()
        self._segments_queue = segments_queue
        self.features_queue = queue.Queue()
        self.print_features = print_features

    """
    Setters/Loaders
    """

    def config_extractor(
        self, features_to_use, output_format="dict_key_per_feature", **kwargs
    ):
        self._featExtractor.config(
            features_to_use, output_format=output_format, **kwargs
        )

    def reset_config_extractor(self):
        self._featExtractor.reset_config()

    """
    Getters
    """

    def get_features_queue(self):
        return self.features_queue

    """
    Workers
    """

    def run(
        self,
    ) -> None:
        "Overwrites method run of base class threading.Thread"
        while True:
            segment = self._segments_queue.get()
            self._featExtractor.load_audio_signal(segment)
            features = self._featExtractor.compute_features_by_config()
            if self.print_features:
                print(features)
            self.features_queue.put(features)
            self._segments_queue.task_done()

    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """


if __name__ == "__main__":
    """
    Used for test purposes
    """

    from MAAP.threads.AudioReceiverThread import AudioReceiverThread

    a = AudioReceiverThread()
    a.config_writer(segment_duration=1)

    f = AudioFeatureExtractorThread(a.get_segments_queue(), print_features=True)
    f.config_extractor(
        ["mfcc", "zero_cross_rate", "spectral_centroid", "spectral_rolloff"],
        mfcc_func_args={"n_mfcc": 13, "pooling": "mean"},
        zero_cross_rate_func_args={"pooling": "mean"},
        spectral_centroid_func_args={"pooling": "mean"},
        spectral_rolloff_func_args={"pooling": "mean"},
    )

    f.setDaemon(True)

    a.start()
    f.start()
    a.join()
    f.join()
