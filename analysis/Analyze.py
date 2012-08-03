#!env python

OUTPUT_DIR = "../output"    # Relative path to output files
CLASS_LABEL = "label"       # Name of the attribute you classify for

import sys
import os
import pickle
import Models

def convert_output_dir(directory):
    """
    Looks in the cwd, parent dir, and sibling dirs for the output directory.
    Calls sys.exit(1) on failed search for output file dir.

    Otherwise, returns the relative path to the output directory.
    
    """

    if not os.path.isdir(directory):
        dirname = os.path.split(directory)[1]
        dircontents = os.listdir(os.getcwd())
        cwd_name = os.path.split(os.getcwd())[1]
        if os.path.isdir(dirname):
            directory = dirname
        elif cwd_name == dirname:
            directory = os.getcwd()
        elif "eeg.py" in dircontents or "README.md" in dircontents:
            print("No output files located.  Exiting!")
            sys.exit(1)
        else:
            sys.stderr.write("""ERROR: Please execute this script
                from its native directory. Exiting!""")
            print("ERROR: Please execute this script from its native directory.")
            sys.exit(1)
    return os.path.relpath(directory)

def get_file_list(path):
    "Returns a list of the files at :path"

    file_list = map(lambda x: os.path.join(path, x), os.listdir(path))
    return file_list

def get_file_contents(files):
    """
    Takes in a list of files :files and attempts to loop over each file.
    For each file, it attempts to unpickle the contents, which should have
    been loaded into the file using the pickle module and the ThinkWave
    connector.

    """

    file_contents = []
    for fn in files:
        file_contents.append(pickle.load(open(fn, "rb")))
    return file_contents

if __name__ == '__main__':
    training_file_dir = convert_output_dir(OUTPUT_DIR)
    training_file_list = get_file_list(training_file_dir)
    training_data = get_file_contents(training_file_list)
    training_set = Models.TrainingSet(CLASS_LABEL, training_data)
    proc = training_set.processor
    # Processor methods:
    # get_point_selection(label=None, user=None, session_number=None, feature=None)
    # get_mean/media/mode/variance/stdev(same as above)
#   print(proc.get_point_selection(feature="theta"))
#   print(training_set.processor.get_points_by_label(label_name="Blue"))
#   print(training_set.processor.get_point_selection(label="Blue", user="daniel", feature="theta"))
#   print(proc.get_stdev(feature="theta", label="Blue", user="daniel"))
    print(proc.get_variance(feature="theta", label="Blue", user="michael"))
    sys.exit(0)

