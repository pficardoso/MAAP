from MAAP.native.AudioSignal import AudioSignal


def concat_audio_signals(audio_signals_list: list):

    # check if all elements in the list are audioSignals
    for element in audio_signals_list:
        if not isinstance(element, AudioSignal):
            raise Exception(
                "All elements in 'audio_signals_list' must be an instance of AudioSignals"
            )

    first_audio_signal = audio_signals_list.pop(0)
    return first_audio_signal + audio_signals_list
