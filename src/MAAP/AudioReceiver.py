import queue
import sys
import warnings

import numpy as np
import sounddevice as sd

from MAAP.AudioSignal import AudioSignal

warnings.simplefilter("always", UserWarning)


class AudioReceiver:
    """"""

    def __init__(self, channels=1, device_id=None):
        """Constructor for AudioReceiver"""
        # Defines device to be used
        if device_id is None:
            device_id = sd.default.device[0]
        if type(device_id) != int:
            raise Exception("Device ID should be int or None")

        self._audio_buffer = np.empty((0, 1))
        self.outQueue = queue.Queue()

        self._device_id = device_id
        self._device_info = sd.query_devices(self._device_id, "input")
        self._sr = self._device_info["default_samplerate"]

        self._channels = 1

        self._segments_duration = None
        self._nr_frames_per_segment = None
        self._is_capturing = False
        self._is_configured = False

        self._audioStream = sd.InputStream(
            samplerate=self._sr,
            blocksize=0,
            device=self._device_id,
            channels=self._channels,
            callback=self._audio_stream_callback,
        )

    def __repr__(self):
        class_name = type(self).__name__

        repr_str = "{}.(sample_rate = {}; " "_outQueue = {};)"

        return repr_str.format(class_name, self._sr, repr(self.outQueue))

    def __enter__(self):
        self._audioStream.__enter__()

    def __exit__(self):
        self._audioStream.__exit__()

    """
    Setters/Loaders
    """

    def config_capture(
        self,
        segments_duration=1,
    ):

        try:
            self._segments_duration = segments_duration
            self._check_segments_duration(segments_duration)
            self._nr_frames_per_segment = int(self._segments_duration * self._sr)
        except Exception as e:
            self._is_configured = False
            print(f"Exception Error while configuring AudioReceiver; Message: {e}")
        else:
            self._is_configured = True

    """
    Getters
    """

    def get_sample_rate(self):
        return self._sr

    def get_sample_from_output_queue(self):
        return self.outQueue.get()

    def get_output_queue(self):
        return self.outQueue

    """
    Workers
    """

    def _audio_stream_callback(self, indata, frames, time, status):
        """
        See callback parameter https://python-sounddevice.readthedocs.io/en/0.4.3/api/streams.html#sounddevice.Stream

        Here, with sd, the samples corresponds to frames.
        The parameter `frames` corresponds to the number of frames/samples collected by sd.InputStream
        """
        if status:
            print(status, file=sys.stderr)
        self._audio_buffer = np.concatenate((self._audio_buffer, indata), axis=0)
        if self._audio_buffer.shape[0] > self._nr_frames_per_segment:
            y, self._audio_buffer = np.split(
                self._audio_buffer, [self._nr_frames_per_segment], axis=0
            )
            signal = AudioSignal(y[:, 0], sample_rate=self._sr)
            self.outQueue.put(signal)
        else:
            pass

    def start(self):

        if not self._is_configured:
            raise Exception("Capture was not configured yet. Run config_capture method")
        self._audioStream.start()

    def abort(self):
        self._audioStream.abort()

    def close(self):
        self._audioStream.close()

    """
    Boolean methods
    """

    def is_capturing(self):
        return self._is_capturing and self._audioStream.active

    def is_configured(self):
        return self._is_configured

    def output_queue_has_samples(self):
        return not self.outQueue.empty()

    """
    Checkers
    """

    """
    Util methods / Static methods
    """

    @staticmethod
    def _check_segments_duration(segments_duration):
        if isinstance(segments_duration, (int, float)):
            if segments_duration >= 0.1 and segments_duration < 1.0:
                # check it is an integer part of one second.
                # The multiplication by 10 is an hack to avoid problems with floating point arithmetic.
                is_intenger_part = (1.0 * 10) % (segments_duration * 10) == 0
                if not is_intenger_part:
                    raise Exception(
                        "Segments duration must be an integer part of 1 second. Ex: 0.25 seconds, or 0.5 seconds"
                    )
            elif segments_duration <= 0.1:
                raise Exception(
                    "Segments duration must be greater or equal than 0.1 seconds"
                )
        else:
            # raise exception
            raise Exception(
                "var segments_duration must be of type int or float. This has type {}".format(
                    type(segments_duration)
                )
            )
