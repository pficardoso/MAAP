import numpy as np

from MAAP.native.AudioReader import AudioReader
from MAAP.native.AudioSignal import AudioSignal

START_TIME_DEFAULT = -1
END_TIME_DEFAULT = -1


class AudioCutter:
    """"""

    def __init__(self, audioSignal=None):
        """

        :param audioSignal:
        :param output_segment_duration: in seconds
        """
        if not audioSignal:  # is None:
            self._has_audio_loaded = False
            pass
        else:
            self.load_audio_signal(audioSignal)

    """
    Setters/Loaders
    """

    def set_output_segment_duration(self, output_segment_duration):
        # validate type
        if not isinstance(output_segment_duration, (int, float, None)):
            raise Exception("output_segment_duration must be None, int or float")

        self._output_segment_duration = output_segment_duration

    def load_audio_signal(self, audioSignal: AudioSignal):
        # check if it is an AudioSignal
        self.audioSignal = audioSignal
        self.y = self.audioSignal.get_data()
        self.sample_rate = self.audioSignal.get_sample_rate()
        self._has_audio_loaded = True

    """
    Getters
    """

    """
    Checkers
    """

    def check_if_audio_signal_is_loaded(self, raise_exception):
        if self._has_audio_loaded:
            return True

        if raise_exception:
            raise Exception("Audio Signal was not loaded yet")

        return False

    def _check_start_and_end_time(self, start_time, end_time):

        if not isinstance(start_time, (int, float)):
            raise Exception(
                "start_time must be of type int or flaot. Type {} was given".format(
                    type(start_time)
                )
            )
        if not isinstance(end_time, (int, float)):
            raise Exception(
                "end_time must be of type int or flaot. Type {} was given".format(
                    type(start_time)
                )
            )

        audio_duration = self.audioSignal.get_duration()
        if start_time == START_TIME_DEFAULT:
            start_time = 0
        else:
            # check if is higher than 0 and lower then audio_duration
            if start_time < 0:
                raise Exception(
                    "start_time must be positive or zero. {} was given.".format(
                        start_time
                    )
                )
            elif start_time > audio_duration:
                raise Exception(
                    "start_time must be lower than audio duration."
                    "start_time of {} and audio_duration {} were given.".format(
                        start_time, audio_duration
                    )
                )
            elif start_time >= end_time:
                raise Exception(
                    "start_time must be lower than end_time."
                    "start_time of {} and end_time {} were given.".format(
                        start_time, end_time
                    )
                )

        if end_time == END_TIME_DEFAULT:
            # check if it has an audioSignal laoded to compute the end_time
            if self.check_if_audio_signal_is_loaded(raise_exception=True):
                end_time = self.audioSignal.get_duration()
        else:
            # check if is higher than 0, higher than start_time, and lower then audio_duration
            if end_time < 0:
                raise Exception(
                    "end_time must be positive or zero. {} was given.".format(
                        start_time
                    )
                )

        return start_time, end_time

    """
    Util methods / Static methods
    """

    """
    Workers
    """

    def cut_audio(self, start_time, end_time):

        # check if it has audio
        self.check_if_audio_signal_is_loaded(raise_exception=True)

        start_time_frame_index = int(start_time * self.audioSignal.get_sample_rate())
        end_time_frame_index = int(end_time * self.audioSignal.get_sample_rate())

        return AudioSignal(
            self.audioSignal.get_data()[start_time_frame_index:end_time_frame_index],
            self.audioSignal.get_sample_rate(),
        )

    def slice_signal_in_n_equal_segments(
        self, n, start_time=START_TIME_DEFAULT, end_time=END_TIME_DEFAULT
    ):

        start_time, end_time = self._check_start_and_end_time(start_time, end_time)

        # compute the duration of each segment
        self.set_output_segment_duration(float((end_time - start_time)) / n)

        # create the audioSignals
        cut_audio_signal_list = list()

        start = start_time
        end = start_time + self._output_segment_duration
        for segment_i in np.arange(0, n):
            cut_audio_signal_list.append(self.cut_audio(start, end))
            start = end
            end = start + self._output_segment_duration

        return cut_audio_signal_list

    def slice_signal_in_multi(
        self,
        output_segment_duration,
        start_time=START_TIME_DEFAULT,
        end_time=END_TIME_DEFAULT,
    ):
        """
        Note: it will ignore the last slice if it does have the output_segment_duration duration
        :param output_segment_duration:
        :param start_time:
        :param end_time:
        :return:
        """
        start_time, end_time = self._check_start_and_end_time(start_time, end_time)
        self.set_output_segment_duration(output_segment_duration)

        # the int operation already does the floor operation
        nr_segments = int(
            float((end_time - start_time)) / self._output_segment_duration
        )

        # create the audioSignals
        cut_audio_signal_list = list()

        start = start_time
        end = start_time + self._output_segment_duration
        for segment_i in np.arange(0, nr_segments):
            cut_audio_signal_list.append(self.cut_audio(start, end))
            start = end
            end = end + self._output_segment_duration

        return cut_audio_signal_list


if __name__ == "__main__":

    audio_file_path = "../../../audio.files/sir_duke_fast.wav"
    audioSignal = AudioReader(audio_file_path).read()

    cutter = AudioCutter()
    cutter.load_audio_signal(audioSignal)

    print("------------- Test function 1 -------------")
    nr_segments = 2
    audios = cutter.slice_signal_in_n_equal_segments(nr_segments, 1.25, 4.25)

    print(audioSignal)
    if len(audios) != nr_segments:
        raise Exception("Error nr 1")

    audioJoined1 = audios[0]
    for audio in audios[1:]:
        audioJoined1 = audioJoined1 + audio

    print("Playing audioSignal {}".format(audioSignal))
    audioSignal.play_audio()
    print("Playing audioJoined1 {}".format(audioJoined1))
    audioJoined1.play_audio()

    print("------------- Test function 2 -------------")
    audios = cutter.slice_signal_in_multi(0.25, 1.25, 4.25)
    print("Nr of segments obtained: {}".format(len(audios)))

    audioJoined2 = audios[0]
    for audio in audios[1:]:
        audioJoined2 = audioJoined2 + audio

    print("Playing audioSignal {}".format(audioSignal))
    audioSignal.play_audio()
    print("Playing audioJoined {}".format(audioJoined2))
    audioJoined2.play_audio()
