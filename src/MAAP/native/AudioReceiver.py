import datetime
import multiprocessing
import queue
import threading
import time
import warnings

import sounddevice as sd

from MAAP.native.AudioSignal import AudioSignal

warnings.simplefilter("always", UserWarning)


class AudioReceiverOutputQueue(queue.Queue):
    """"""

    def __init__(self, maxsize_seconds, segments_duration):
        """

        :param maxsize:
        """
        if maxsize_seconds is None:
            maxsize_seconds = 0  # size is infinite

        if segments_duration is None:
            raise Exception("segments_duration arg must be given")

        if maxsize_seconds != 0 and maxsize_seconds < segments_duration:
            raise Exception(
                "Size of buffer (maxsize_seconds arg), in seconds, must be larger than  the duration of a "
                "single segment (segments_duration arg)"
            )

        self._max_nr_signals = maxsize_seconds / segments_duration
        super().__init__(self._max_nr_signals)
        self._maxsize_seconds = maxsize_seconds
        self._segment_duration = segments_duration
        self._capture_is_configured = False

    def get_maxsize_seconds(self):
        return self._maxsize_seconds

    def __repr__(self):
        class_name = type(self).__name__
        repr_str = (
            "{}.(maxsize_duration = {}; "
            "segment_duration = {}; "
            "max_nr_signals = {}; "
            "current_duration = {}; "
            "current_nr_signals = {};)"
        )

        current_nr_signals = self.qsize()
        current_duration = current_nr_signals * self._segment_duration
        print(datetime.timedelta(seconds=current_duration))
        return repr_str.format(
            class_name,
            datetime.timedelta(seconds=self._maxsize_seconds),
            datetime.timedelta(seconds=self._segment_duration),
            self._max_nr_signals,
            datetime.timedelta(seconds=current_duration),
            current_nr_signals,
        )

    def _concat_signal_elements(self):
        list_audio = list(self.queue)
        megaAudioSignal = list_audio[0]
        for audioSignalIns in list_audio[1:]:
            megaAudioSignal = megaAudioSignal + audioSignalIns
        return megaAudioSignal

    def play_queue(self, concat_elements=True):

        if concat_elements:
            mega_audio = self._concat_signal_elements()
            print("Playing Mega Audio")
            print("Duration", mega_audio.get_duration())
            mega_audio.play_audio()
        else:
            list_audio = list(self.queue)
            for idx, audio_signal in enumerate(list_audio):
                print("Playing signal nr", idx)
                print("Duration", audio_signal.get_duration())
                audio_signal.play_audio()

    def plot_queue_signal(self):
        mega_audio = self._concat_signal_elements()
        mega_audio.plot_signal()


class AudioReceiver:
    """"""

    STOP_CAPTURE_MODE_LIST = ["default", "timeout", "by_command", "by_parent"]
    TIMEOUT_DURATION_DEFAULT = 20  # 20 seconds

    def __init__(self, channels=1, device_id=None):
        """Constructor for AudioReceiver"""
        # Defines device to be used
        if device_id is None:
            device_id = sd.default.device[0]
        if type(device_id) != int:
            raise Exception("Device ID should be int or None")

        self._device_id = device_id
        self._device_info = sd.query_devices(self._device_id, "input")
        self.sr = self._device_info["default_samplerate"]

        # Number of channels
        self.channels = 1
        self._is_capturing = False
        self._input_stream = None
        self._outputQueue = None

        self._stop_condition = None
        self._stop_condition_params = None
        self._segments_duration = None
        self._capture_thread = None
        self._capture_is_configured = False

    def __repr__(self):
        class_name = type(self).__name__

        repr_str = "{}.(sample_rate = {}; " "stop_conditon = {}; " "_outputQueue = {};)"

        return repr_str.format(
            class_name, self.sr, self._stop_condition, repr(self._outputQueue)
        )

    def get_sample_rate(self):
        return self.sr

    def get_stop_condition_parameters(self):
        return self._stop_condition_params

    def get_length_buffer_seconds(self):
        return self._outputQueue.get_maxsize_seconds()

    def _configure_input_stream(self, callback=None):

        self._input_stream = sd.InputStream(
            samplerate=self.sr,
            blocksize=0,
            device=self._device_id,
            channels=self.channels,
            callback=callback,
        )

    def _set_and_check_stop_condition(self, stop_condition):
        # Check if stop conditions exists
        if stop_condition in AudioReceiver.STOP_CAPTURE_MODE_LIST:
            if stop_condition == "default":
                self._stop_condition = "timeout"
                return
            else:
                self._stop_condition = stop_condition
                return
        else:
            raise Exception(
                "The selected stop condition '{}' doest not exist. Select one of the following {}".format(
                    stop_condition, AudioReceiver.STOP_CAPTURE_MODE_LIST
                )
            )

    def _set_and_check_stop_conditions_params(self, segments_duration, params: dict):

        stop_condition_params = dict()
        if self._stop_condition == "timeout":
            # check conditions for timeout:
            # 1 - See if parameters exist
            # 2 - timeout_duration must be greater than twice of audio_segment
            if "timeout_duration" in params:
                stop_condition_params["timeout_duration"] = params["timeout_duration"]
            else:
                stop_condition_params[
                    "timeout_duration"
                ] = AudioReceiver.TIMEOUT_DURATION_DEFAULT
                warnings.warn(
                    "Timeout duration default value ( {} seconds) will be used".format(
                        AudioReceiver.TIMEOUT_DURATION_DEFAULT
                    )
                )
            if stop_condition_params["timeout_duration"] < 2 * segments_duration:
                raise Exception(
                    "'Timeout duration' must be greater than the double of 'segments_duration'"
                )

        self._stop_condition_params = stop_condition_params

    def _get_keep_capturing_thread_or_process(
        self, stop_condition, stop_condition_params
    ):
        def keep_capturing_timeout_mode_function(params):
            while time.time() < time_start + params["timeout_duration"]:
                pass

        def keep_capturing_by_command_mode_function(params):
            print("Write 'stop' to stop the process")
            command_selected = False
            while not command_selected:
                val = input()
                if val.strip() == "stop":
                    command_selected = True

        def keep_capturing_by_parent_mode_function():
            while True:
                pass

        if stop_condition == "timeout":
            time_start = time.time()
            return multiprocessing.Process(
                target=keep_capturing_timeout_mode_function,
                args=(stop_condition_params,),
                daemon=True,
            )

        if stop_condition == "by_command":
            return threading.Thread(
                target=keep_capturing_by_command_mode_function,
                args=(stop_condition_params,),
                daemon=True,
            )

        if stop_condition == "by_parent":
            return multiprocessing.Process(
                target=keep_capturing_by_parent_mode_function, daemon=False
            )

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

    def config_capture(
        self,
        stop_condition="default",
        segments_duration=1,
        buffer_size_seconds=0,
        daemon=True,
        stop_parameters=dict(),
    ):

        self._segments_duration = segments_duration
        self._check_segments_duration(segments_duration)
        self._set_and_check_stop_condition(stop_condition)
        self._outputQueue = AudioReceiverOutputQueue(
            buffer_size_seconds, segments_duration
        )
        self._configure_input_stream()
        self._set_and_check_stop_conditions_params(segments_duration, stop_parameters)

        # initialize capture_thread
        keep_alive_thread = self._get_keep_capturing_thread_or_process(
            self._stop_condition, self._stop_condition_params
        )
        nr_frames_per_segment = int(self._segments_duration * self.sr)
        self._capture_thread = threading.Thread(
            target=self._capture_thread_target_function,
            args=(keep_alive_thread, nr_frames_per_segment),
            daemon=daemon,
        )
        self._capture_is_configured = True

    def start_capture(self):

        if not self._capture_is_configured:
            raise Exception("Capture was not configured yet. Run config_capture method")
        self._capture_thread.start()

    def capture_join(self):
        self._capture_thread.join()

    def _capture_thread_target_function(self, keep_alive_thread, nr_frames_per_segment):

        with self._input_stream:
            print(
                "Capturing with stop condition '{}' and params {}".format(
                    self._stop_condition, self._stop_condition_params
                )
            )
            self._is_capturing = True
            keep_alive_thread.start()
            while keep_alive_thread.is_alive():
                """
                data is  a two-dimensional numpy.ndarray with one column per channel (shape of
                (frames, channels)). The AudioSignal class must receive a np.array with len nr_frames.
                Thus, it is transposed.
                """
                data, _ = self._input_stream.read(nr_frames_per_segment)
                try:
                    self._outputQueue.put(
                        AudioSignal(data.transpose()[0], self.sr), block=False
                    )
                except queue.Full:
                    warnings.warn(
                        "OutputQueue is full. AudioSignal entering on queue was deleted."
                    )
            self._is_capturing = False
        return

    def is_capturing(self):
        return self._is_capturing

    def output_queue_has_samples(self):
        return not self._outputQueue.empty()

    def get_sample_from_output_queue(self):
        return self._outputQueue.get()

    def get_output_queue(self):
        return self._outputQueue

    def join_output_queue(self):
        return self._outputQueue.join()


if __name__ == "__main__":

    audioReceiver = AudioReceiver()

    # ------------Test 1-------------
    audioReceiver.config_capture(
        "by_parent",
    )
    audioReceiver.start_capture()
    audioReceiver._outputQueue.plot_queue_signal()
    print(repr(audioReceiver._outputQueue))
    print(repr(audioReceiver))
