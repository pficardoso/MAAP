import sys
sys.path.append("../.")

from src.resources.FSCrawler.FSCrawler import FSCrawler
from src.MAAP.native.AudioFeatureExtractor import AudioFeatureExtractor
import pickle
import os
import argparse
from tqdm import tqdm

EXTENSION = ".wav"

example_text="" \
             "Examples:\n" \
             "-d ../. -l 2\n" \
             "-d ../."

parser = argparse.ArgumentParser(description="Feature extraction of audios files and pickles creation", epilog=example_text, formatter_class = argparse.RawTextHelpFormatter)
parser.add_argument("-d", "--dir",  required=True, type=str, help="Root directory path in which audio files will be searched and processed")
parser.add_argument("-l", "--level", default=-1, type=int, help="Max depth with the audio files will be searched. With -1 value it will search without depth restrictions")


if __name__=="__main__":

    args = parser.parse_args()

    root_dir = args.dir

    level    = args.level

    fsCrawler = FSCrawler(root_dir)
    featureExtractor = AudioFeatureExtractor()

    list_audios_paths = fsCrawler.search_files(extension=EXTENSION, max_depth=level)

    ## Should iterate over audio_files. For each one of them, make a pickle with in the dir.
    for audio_file_path in tqdm(list_audios_paths, ncols=100):
        ##obtain features
        featureExtractor.load_audio_file(audio_file_path)
        features = featureExtractor.compute_all_features()

        ## compute the final path for the pickle
        audio_file_dir   = os.path.dirname(audio_file_path)
        pickle_file_name = "".join( [os.path.basename(audio_file_path)[:-len(EXTENSION)], ".ft.pickle"] )
        pickle_file_path = os.path.join(audio_file_dir, pickle_file_name)

        pickle.dump(  features, open( pickle_file_path , "wb" ))


