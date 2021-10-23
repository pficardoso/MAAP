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

import argparse
import datetime
import json
import os
import time

import git

from src.MAAP.native.AudioReceiver import AudioReceiver
from src.resources.FSHandler import FSHandler

FATHER_DIR_NAME = "../data.acquisition/"
SUBFOLDER_PREFIX = "set"
REPORT_FILE_NAME = "report.txt"

example_text = (
    ""
    "Examples:\n"
    "Running in 'timeout' stop condition example -> -d test -t 2 -s timeout  -sp '{\"timeout_duration\":15}'\n"
    "Running in 'by_command' stop condition example -> -d test -t 2 -s by_command\n"
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
    "-t",
    "--time",
    required=True,
    type=float,
    help="Duration of audio segments, in seconds",
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


def capture(
    dir_name,
    segments_duration,
    stop_condition,
    stop_condition_parameters,
    buffer_size_duration,
):

    audioReceiver = AudioReceiver()
    audioReceiver.config_capture(
        stop_condition,
        segments_duration,
        buffer_size_duration,
        True,
        stop_condition_parameters,
    )

    # waits two seconds to allow initialization of thread until audioReceiver
    # starts capture
    audioReceiver.start_capture()
    time.sleep(1)
    counter_audios_recorded = 0
    while audioReceiver.is_capturing() or audioReceiver.output_queue_has_samples():
        counter_audios_recorded = counter_audios_recorded + 1

    # This last join is not necessary probably, but will be done just for precaution
    audioReceiver.capture_join()
    return audioReceiver, counter_audios_recorded


def make_report(
    capture_name,
    dir_name,
    run_date,
    stop_condition,
    segment_duration,
    audioReceiver: AudioReceiver,
    nr_audios_recorded,
):
    report = dict()
    report["name"] = capture_name
    report["date"] = run_date
    report["audio_sample_rate"] = "{} Hz".format(audioReceiver.get_sample_rate())
    report["stop_condition"] = stop_condition
    report["stop_parameters"] = audioReceiver.get_stop_condition_parameters()

    buffer_size_seconds = audioReceiver.get_length_buffer_seconds()
    if buffer_size_seconds == 0:
        buffer_size_str = "inf"
    else:
        buffer_size_str = get_str_minutes_second(buffer_size_seconds)

    report["buffer_size"] = buffer_size_str
    report["audio_segment_duration"] = get_str_minutes_second(segment_duration)
    report["total_segments_acquired"] = nr_audios_recorded
    total_time_acquired_seconds = segment_duration * nr_audios_recorded
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
    audioReceiver, nr_audios_recorded = capture(
        dir_to_save,
        args.time,
        args.stop_condition,
        args.stop_parameters,
        args.buffer_size,
    )

    make_report(
        args.dir,
        dir_to_save,
        run_date,
        args.stop_condition,
        args.time,
        audioReceiver,
        nr_audios_recorded,
    )
    print("End")
