"""
Script to record audio and save it on a folder

Requirements:
    - Parameters of the program
        - Path of directory where audio files will be saved
        - Stop condition
        - Stop parameters
        - Size of the AudioReceiverBuffer

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

import argparse
import datetime
import json
import os
import time

import git

from src.MAAP.native.AudioReceiver import AudioReceiver
from src.MAAP.native.AudioWriter import AudioWriter
from src.MAAP.native.UtilsMAAP import concat_audio_signals
from src.resources.FSHandler import FSHandler

FATHER_DIR_NAME = "../data.acquisition/"
SUBFOLDER_PREFIX = "set"
REPORT_FILE_NAME = "report.txt"
SEGMENTS_DURATION = 0.25
OUTPUT_AUDIO_FILENAME = "all.wav"

example_text = (
    ""
    "Examples:\n"
    "Running in 'timeout' stop condition example -> -d test -s timeout  -sp '{\"timeout_duration\":15}'\n"
    "Running in 'by_command' stop condition example -> -d test -s by_command\n"
)
parser = argparse.ArgumentParser(
    description="Acquire audio files",
    epilog=example_text,
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
    "-d", "--dir", required=True, help="Path of dir where audio files should be saved"
)
parser.add_argument(
    "-s", "--stop-condition", required=True, help="Stop condition of capture"
)
parser.add_argument(
    "-sp",
    "--stop-parameters",
    type=json.loads,
    help="Stop condition parameters - json input",
)
parser.add_argument(
    "-b",
    "--buffer-size",
    required=False,
    type=int,
    help="Size of audio buffer, in seconds",
)


def get_current_date_time():

    # datetime object containing current date and time
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string


def get_str_minutes_second(seconds: int):
    return "{} ({} seconds)".format(datetime.timedelta(seconds=seconds), seconds)


def capture(dir_name, stop_condition, stop_condition_parameters, buffer_size_duration):

    dir = os.path.join(FATHER_DIR_NAME, dir_name)
    audioReceiver = AudioReceiver()
    audioReceiver.config_capture(
        stop_condition,
        SEGMENTS_DURATION,
        buffer_size_duration,
        True,
        stop_condition_parameters,
    )

    # waits two seconds to allow initialization of thread until audioReceiver
    # starts capture
    audioReceiver.start_capture()
    time.sleep(1)
    counter_segments_recorded = 0
    audio_signals = list()
    while audioReceiver.is_capturing() or audioReceiver.output_queue_has_samples():
        counter_segments_recorded = counter_segments_recorded + 1
        audio_signals.append(audioReceiver.get_sample_from_output_queue())

    # write the audioSignal audio
    audioWriter = AudioWriter(
        dir, OUTPUT_AUDIO_FILENAME, concat_audio_signals(audio_signals)
    )
    audioWriter.write()
    return audioReceiver, counter_segments_recorded


def make_report(
    capture_name,
    dir_name,
    run_date,
    stop_condition,
    audioReceiver: AudioReceiver,
    nr_segments_recorded,
):
    report = dict()
    report["name"] = capture_name
    report["date"] = run_date
    report["script"] = os.path.relpath(__file__, "../")
    report["audio_sample_rate"] = "{} Hz".format(audioReceiver.get_sample_rate())
    report["stop_condition"] = stop_condition
    report["stop_parameters"] = audioReceiver.get_stop_condition_parameters()

    buffer_size_seconds = audioReceiver.get_length_buffer_seconds()
    if buffer_size_seconds == 0:
        buffer_size_str = "inf"
    else:
        buffer_size_str = get_str_minutes_second(buffer_size_seconds)

    report["buffer_size"] = buffer_size_str
    report["audio_segment_duration"] = get_str_minutes_second(SEGMENTS_DURATION)
    report["total_segments_acquired"] = nr_segments_recorded
    total_time_acquired_seconds = SEGMENTS_DURATION * nr_segments_recorded
    report["total_time_acquired"] = get_str_minutes_second(total_time_acquired_seconds)
    report["MAAP_commit_sha"] = git.Repo("../.").head.commit

    with open(os.path.join(dir_name, REPORT_FILE_NAME), "w") as file_writer:
        for key, value in report.items():
            file_writer.write("{}:\t{}\n".format(key, str(value)))


if __name__ == "__main__":

    args = parser.parse_args()
    dir_to_save = os.path.join(FATHER_DIR_NAME, args.dir)

    fsHandler = FSHandler()
    fsHandler.mkdir_preserve_content(dir_to_save, "set")

    run_date = get_current_date_time()

    print("Audio is being recorded")
    audioReceiver, nr_segments_recorded = capture(
        dir_to_save, args.stop_condition, args.stop_parameters, args.buffer_size
    )

    make_report(
        args.dir,
        dir_to_save,
        run_date,
        args.stop_condition,
        audioReceiver,
        nr_segments_recorded,
    )
    print("End")
