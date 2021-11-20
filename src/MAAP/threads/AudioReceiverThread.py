from MAAP.AudioReceiver import AudioReceiver


class AudioReceiverThread:
    """
    Basically pretends the run of MAAP.AudioReceiver as a threading.Thread objects. For this reason,
    the AudioReceiver used in this class runs always with stop_mode_capture of "by_command"
    """

    def __init__(
        self,
    ):
        """Constructor for AudioReceiverQueue"""
        self._audioReceiver = AudioReceiver()
        self.segments_queue = None

    """
    Setters/Loaders
    """

    def config_writer(
        self,
        segment_duration=None,
        segments_duration=1,
        buffer_size_seconds=0,
        daemon=True,
        stop_parameters=dict(),
    ):
        self._audioReceiver.config_capture(
            "by_command",
            segments_duration=segments_duration,
            buffer_size_seconds=buffer_size_seconds,
            daemon=daemon,
            stop_parameters=stop_parameters,
        )
        self.segments_queue = self._audioReceiver._outputQueue

    """
    Getters
    """

    def get_segments_queue(self):
        if self._audioReceiver._capture_is_configured:
            return self.segments_queue
        raise Exception("Audio Receiver is not configured yet")

    """
    Workers
    """

    def start(self):
        self._audioReceiver.start_capture()

    def join(self):
        self._audioReceiver.capture_join()

    """
    Boolean methods
    """

    """
    Checkers
    """

    """
    Util methods / Static methods
    """
