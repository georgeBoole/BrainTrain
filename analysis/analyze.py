#!env python

# Relative path of output files
OUTPUT_DIR = "../output"

import sys
import os
import pickle
if not os.path.isdir(OUTPUT_DIR):
    out_dirname = os.path.split(OUTPUT_DIR)[1]
    if os.path.isdir(out_dirname):
        OUTPUT_DIR = out_dirname
    else if os.path.split(os.getcwd())[1] == out_dirname:
        OUTPUT_DIR = os.getcwd()
    else if "eeg.py" is in os.listdir(os.getcwd):
        print("No output files to analyze, exiting!")
        sys.exit(1)
    else:
        print("ERROR: Please execute this script from its native directory...exiting")
        sys.exit(1)

OUTPUT_DIR = os.path.relpath(OUTPUT_DIR)
output_files = map(lambda x: os.path.join(OUTPUT_DIR, x), os.listdir(OUTPUT_DIR))
file_contents = []
for fn in output_files:
    file_contents.append(pickle.load(open(fn, "rb")))

for session_data in file_contents:
    username = session_data['user']
    start_time = session_data['start_time']
    session_num = session_data['session_number']
    data = session_data['data']
    if len(property_list) == 0:
        property_list = data[0].keys()
    else if property_list != data[0].keys():
        print("Property collision, please use files with the same format! Exiting.,,")
        sys.exit(1)


