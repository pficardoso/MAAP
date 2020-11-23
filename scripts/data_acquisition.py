"""
Script to record audio and save it on a folder

Requirements:
    - Parameters of the program
        - Path of directory where audio files will be saved
        - Size of audio segments in seconds (i.e. duration of final audio files)
        - Size of the AudioReceiverBuffer
        - Mode of capture
        - Parameters of capture's mode

Some features:
    - The directory where files are saved must be a descendant of dir '../data.acquisition/'
    - If the directory does not exist, must be created
    - If the directory already exists:
        1 - a warning bust be raised
        2 - previous files in that directory must be moved to a daughter folder (to be created)
    - Write a report of the recording session
"""

from src.MAAP.native.AudioReceiver import AudioReceiver
from src.MAAP.native.AudioWriter import AudioWriter
import argparse
import threading
import time
import os


FATHER_DIR_NAME = '../data.acquisition/'


def capture():

    dir = os.path.join(FATHER_DIR_NAME, dir_name)
    audioReceiver = AudioReceiver()
    capture_thread = threading.Thread(target=audioReceiver.start_capture,
                                      args=(capture_mode, segments_duration, buffer_size_duration),
                                      kwargs=capture_mode_parameters)
    capture_thread.start()

    # waits two seconds to allow initialization of thread until audioReceiver
    # starts capture
    time.sleep(1)
    c=0
    while (audioReceiver.is_capturing()) or (audioReceiver.buffer_has_samples()):
        if not audioReceiver.buffer_has_samples():
            c=c+1
            audio_signal = audioReceiver.get_sample_from_buffer()
            AudioWriter(dir, str(c)+".wav", audio_signal).write()

if __name__=="__main__":
    #TODO:
    # 1 - get parameters
    # 2 - validate parameters
    # 3 - create directory where files will be saved
    # 4 - start recording

    capture_mode = "timeout"
    segments_duration = 2
    buffer_size_duration = 10
    dir_name = 'test'
    capture_mode_parameters = {'timeout_duration': 8}
    print("Audio is being recorded")
    capture()
    print("End")

