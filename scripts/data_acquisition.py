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
import sys
sys.path.append("../.")

from src.MAAP.native.AudioReceiver import AudioReceiver
from src.MAAP.native.AudioWriter import AudioWriter
import argparse
import threading
import time
import os
import re
import json

FATHER_DIR_NAME = '../data.acquisition/'
SUBFOLDER_PREFIX = 'set'

example_text="" \
             "Examples:\n" \
             "Running in 'timeout' stop condition example -> -d test -t 2 -s timeout  -sp \'{\"timeout_duration\":15}\'\n" \
             "Running in 'by_command' stop condition example -> -d test -t 2 -s by_command\n" \

parser = argparse.ArgumentParser(description="Acquire audio files", epilog=example_text, formatter_class = argparse.RawTextHelpFormatter)
parser.add_argument("-d", "--dir",  required=True, help="Path of dir where audio files should be saved")
parser.add_argument("-t", "--time", required=True, type=int, help="Duration of audio segments, in seconds")
parser.add_argument("-s", "--stop-condition", required=True, help="Stop condition of capture")
parser.add_argument("-sp", "--stop-parameters", type=json.loads, help="Stop condition parameters - json input")
parser.add_argument("-b", "--buffer-size", required=False, type=int, help="Size of audio buffer, in seconds")


def prepare_folders(dir_name):


    if len(dir_name.split("/"))>1:
        raise Exception("dir_name {} must only have one level".format(dir_name))

    ## if the dir_name does not exists, create the folder
    path_to_use = os.path.join(FATHER_DIR_NAME, dir_name)

    if not os.path.isdir(path_to_use):
        os.makedirs(path_to_use)
    else:
        ## creates the subfolder and move existent.wav files to them
        create_subfolder = False
        highest_folder_number = 0
        wav_files_list = list()
        ## obtain .wav files; and the defines the number of the new folder to be created
        regexp_folder_tmp = '{}.[0-9]+'.format(SUBFOLDER_PREFIX)
        for file_dir_name in os.listdir(path_to_use):
            fir_dir_path = os.path.join(path_to_use, file_dir_name)
            if os.path.isfile(fir_dir_path) and os.path.splitext(file_dir_name)[1] == ".wav":
                create_subfolder = True
                wav_files_list.append(fir_dir_path)
            elif os.path.isdir(fir_dir_path) and re.search(regexp_folder_tmp, file_dir_name):
                folder_number = int(file_dir_name.split(".")[1])
                if folder_number > highest_folder_number:
                    highest_folder_number = folder_number

        if create_subfolder:
            ## creates the subfolder
            dir_to_move = os.path.join(path_to_use, '{}.{}'.format(SUBFOLDER_PREFIX, highest_folder_number+1))
            os.mkdir(dir_to_move)
            ## move files
            for wav_file_path in wav_files_list:
                src = wav_file_path
                wav_file_name = os.path.basename(src)
                target = os.path.join(dir_to_move, wav_file_name)
                os.rename(src, target)

    return path_to_use



def capture( dir_name, segments_duration, stop_condition, stop_condition_parameters, buffer_size_duration,):

    dir = os.path.join(FATHER_DIR_NAME, dir_name)
    audioReceiver = AudioReceiver()
    capture_thread = threading.Thread(target=audioReceiver.start_capture,
                                      args=(stop_condition, segments_duration, buffer_size_duration),
                                      kwargs=stop_condition_parameters)
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

    args = parser.parse_args()

    final_dir = prepare_folders(args.dir)

    print("Audio is being recorded")
    capture(final_dir, args.time,
            args.stop_condition, args.stop_parameters, args.buffer_size)

    print("End")

