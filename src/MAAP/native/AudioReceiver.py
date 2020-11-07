import sounddevice as sd
import queue
import sys
import time
import numpy as np
from src.MAAP.native.AudioSignal import AudioSignal


class AudioReceiverOutputQueue(queue.Queue):
    """"""
    def __init__(self, maxsize):
        """Constructor for AudioReceiverOutputQeueu"""
        super().__init__(maxsize)


    def _concat_signal_elements(self):
        list_audio = list(self.queue)
        mega_audio_data = list()
        for idx, audio_signal in enumerate(list_audio):
            mega_audio_data.extend(audio_signal.y)
        mega_audio = AudioSignal(np.array(mega_audio_data), list_audio[0].sr)
        return mega_audio

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

class AudioSampleBucket():
    """"""

    def __init__(self,):
        """Constructor for AudioSampleBucket"""
        self._data = list()

    def clear(self):
        self._data.clear()

    def get_all_data(self, clean_bucket, datatype=np.array, ):

        if not isinstance(clean_bucket, bool):
            raise Exception("Clean_bucket should be a boolean")

        if datatype==list:
            return self._data
        elif datatype in set([np.array]):
            output = datatype(self._data)
        else:
            raise Exception("The selected type is not allowed")

        if clean_bucket:
            self.clear()

        return output

    def add(self, data_sample):
        self._data.append(data_sample)

class AudioReceiver():
    """"""
    STOP_CAPTURE_MODE = ["default","timeout"]
    TIMEOUT_DURATION_DEFAULT = 3 # 3 seconds

    def __init__(self, channels=1, device_id=0):
        """Constructor for AudioReceiver"""
        ## Defines device to be used
        self._device_id = device_id
        self._device_info =  sd.query_devices(self._device_id, 'input')
        self.sr = self._device_info['default_samplerate']

        ## Number of channels
        self.channels=1
        self.is_capturing = False
        self._data_samples_bucket = AudioSampleBucket()
        self._input_stream = None
        self._outputQueue = None

        self._stop_condition = None
        self._stop_condition_params = None

    def _configure_input_stream(self, callback=None):

        if not callback:
            callback = self._get_input_stream_callback(0)

        self._input_stream = sd.InputStream(samplerate=self.sr,
                                            blocksize=0,
                                            device=self._device_id,
                                            channels=self.channels,
                                            callback=callback,
                                            )

    def _get_input_stream_callback(self, mode=0):


        def callback_mode_0(indata, frame, time, status):
            if status:
                print(status, file=sys.stderr)

            for data_sample in indata:
                self._data_samples_bucket.add(data_sample[0])

        if mode==0:
            callback_function = callback_mode_0
        else:
            raise("The selected mode", mode, "does not exist")

        return callback_function

    def capture_n_signals(self, n=1, signal_duration=1):
        """
        :param n:
        :param duration_seconds:
        :return: returns an array of n audio_signals
        """

        audio_signal_array = list()
        self._data_samples_bucket.clear()
        self._configure_input_stream(self._get_input_stream_callback(0))

        with self._input_stream:
            self.is_capturing = True
            for i in range(0, n):
                time.sleep(signal_duration)
                audio_signal_array.append(AudioSignal(self._data_samples_bucket.get_all_data(True), self.sr))
        self.is_capturing = False

        return audio_signal_array

    def _set_and_check_stop_condition(self, stop_condition):
        ## Check if stop conditions exists
        if stop_condition in AudioReceiver.STOP_CAPTURE_MODE:
            if stop_condition == "default":
                self._stop_condition = "timeout"
                return
            else:
                self._stop_condition = stop_condition
                return
        else:
            raise Exception("The selected stop condition '{}' doest not exist. Select one of the following {}".format(
                stop_condition, AudioReceiver.STOP_CAPTURE_MODE
            ))

    def _set_and_check_stop_conditions_params(self, segments_duration, params):

        stop_condition_params = dict()
        if self._stop_condition == "timeout":
            ## check conditions for timeout:
            ## 1 - See if parameters exist
            ## 2 - timeout_duration must be greater than twice of audio_segment
            stop_condition_params["time_start"] = time.time()
            if "timeout_duration" in params:
                stop_condition_params["timeout_duration"] = params["timeout_duration"]
            else:
                stop_condition_params["timeout_duration"] = AudioReceiver.TIMEOUT_DURATION_DEFAULT
            if stop_condition_params["timeout_duration"] < 2*segments_duration:
                raise Exception("'Timeout duration' must be greater than the double of 'segments_duration'")

        self._stop_condition_params = stop_condition_params

    @staticmethod
    def _get_keep_capturing_function(stop_condition):

        def is_inside_timeout(params):
            return time.time() < params["time_start"] + params["timeout_duration"]

        ## if stop_condition is timeout
        if stop_condition == "timeout":
            return is_inside_timeout

    def start_capture(self, stop_condition="default", segments_duration=1, buffer_max_size=0, **kargs):

        ##set stops condition
        self._set_and_check_stop_condition(stop_condition)
        ##initialization of output queue
        self._outputQueue = AudioReceiverOutputQueue(buffer_max_size)
        ##configures input stream
        self._configure_input_stream(self._get_input_stream_callback(0))
        ##get params of stop condition
        self._set_and_check_stop_conditions_params(segments_duration, kargs)

        with self._input_stream:
            print("Capturing with stop condition '{}' and params {}".format(self._stop_condition, self._stop_condition_params) )
            self.is_capturing = True
            keep_capturing_function = self._get_keep_capturing_function(self._stop_condition)
            while keep_capturing_function(self._stop_condition_params):
                ## captures signal during 'segments_duration' seconds
                time.sleep(segments_duration)
                ## Crete a AudioSignal instance with the captured data and stores it in Queue.
                self._outputQueue.put(AudioSignal(self._data_samples_bucket.get_all_data(True), self.sr))

if __name__ == "__main__":

    audioReceiver = AudioReceiver()

    ##------------Test 1-------------

    audioReceiver.start_capture("timeout", 1, buffer_max_size=10)
    audioReceiver._outputQueue.play_queue()
    audioReceiver._outputQueue.plot_queue_signal()


    ##-----------Test 2-------------
    """
    audio_signals = audioReceiver.capture_n_signals(2, 2)
    for idx, audio_signal in enumerate(audio_signals):
        print("playing signal nr", idx)
        print("duration", audio_signal.get_duration())
        audio_signal.play_audio()
    """



