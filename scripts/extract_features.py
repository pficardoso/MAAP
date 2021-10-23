import os
import sys

"""
adds the abspath of MAAP source root to the syspath.
"""
sys.path.append(os.path.abspath(os.path.join(__file__, "../..")))


import argparse
import pickle

from tqdm import tqdm

from src.MAAP.native.AudioFeatureExtractor import AudioFeatureExtractor
from src.resources.FSCrawler.FSCrawler import FSCrawler

EXTENSION = ".wav"

example_text = "" "Examples:\n" "-d ../. -l 2\n" "-d ../."

parser = argparse.ArgumentParser(
    description="Feature extraction of audios files and pickles creation",
    epilog=example_text,
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
    "-d",
    "--dir",
    required=True,
    type=str,
    help="Root directory path in which audio files will be searched and processed",
)
parser.add_argument(
    "-l",
    "--level",
    default=-1,
    type=int,
    help="Max depth with the audio files will be searched. With -1 value it will search without depth restrictions. "
    "Default value is -1",
)
parser.add_argument(
    "--uniq_pickle",
    action="store_true",
    help="It will create a uniq pickle file for all the audio files. The pickle file will be saved in the path "
    "given by -d/--dir",
)


def extract_features_and_make_uniq_pickle(list_audios_paths, dir_to_save):
    list_audios_features = []
    for audio_file_path in tqdm(list_audios_paths, ncols=100):
        # obtain features
        featureExtractor.load_audio_file(audio_file_path)
        features = featureExtractor.compute_all_features()
        list_audios_features.append((audio_file_path, features))

    # compute the final path for the pickle
    pickle_file_name = "all.ft.pickle"
    pickle_file_path = os.path.join(dir_to_save, pickle_file_name)

    pickle.dump(list_audios_features, open(pickle_file_path, "wb"))


def extract_features_and_make_feature_per_file(list_audios_paths):
    # Should iterate over audio_files. For each one of them, make a pickle with in the dir.
    for audio_file_path in tqdm(list_audios_paths, ncols=100):
        # obtain features
        featureExtractor.load_audio_file(audio_file_path)
        features = featureExtractor.compute_all_features()

        # compute the final path for the pickle
        audio_file_dir = os.path.dirname(audio_file_path)
        pickle_file_name = "".join(
            [os.path.basename(audio_file_path)[: -len(EXTENSION)], ".ft.pickle"]
        )
        pickle_file_path = os.path.join(audio_file_dir, pickle_file_name)

        pickle.dump((audio_file_path, features), open(pickle_file_path, "wb"))


if __name__ == "__main__":

    args = parser.parse_args()

    root_dir = args.dir

    level = args.level

    fsCrawler = FSCrawler(root_dir)
    featureExtractor = AudioFeatureExtractor()

    list_audios_paths = fsCrawler.search_files_by_extension(
        extension=EXTENSION, max_depth=level
    )

    if args.uniq_pickle:
        # stores in a uniq pickle
        extract_features_and_make_uniq_pickle(list_audios_paths, root_dir)
    else:
        # stores a pickle per audio_file
        extract_features_and_make_feature_per_file(list_audios_paths)
