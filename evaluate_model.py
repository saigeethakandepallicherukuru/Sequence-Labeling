#!/usr/bin/env python3

__author__ = "Sai Geetha Kandepalli Cherukuru"
__email__ = "kandepal@usc.edu"

from collections import namedtuple
import csv
import glob
import os
import sys

def get_utterances_from_file(dialog_csv_file):
    """Returns a list of DialogUtterances from an open file."""
    reader = csv.DictReader(dialog_csv_file)
    return [_dict_to_dialog_utterance(du_dict) for du_dict in reader]

def get_utterances_from_filename(dialog_csv_filename):
    """Returns a list of DialogUtterances from an unopened filename."""
    with open(dialog_csv_filename, "r") as dialog_csv_file:
        return get_utterances_from_file(dialog_csv_file)

def get_data(data_dir):
    """Generates lists of utterances from each dialog file.

    To get a list of all dialogs call list(get_data(data_dir)).
    data_dir - a dir with csv files containing dialogs"""
    dialog_filenames = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    for dialog_filename in dialog_filenames:
        yield get_utterances_from_filename(dialog_filename)

DialogUtterance = namedtuple("DialogUtterance", ("act_tag", "speaker", "pos", "text"))

PosTag = namedtuple("PosTag", ("token", "pos"))

def _dict_to_dialog_utterance(du_dict):
    """Private method for converting a dict to a DialogUtterance."""

    # Remove anything with 
    for k, v in du_dict.items():
        if len(v.strip()) == 0:
            du_dict[k] = None

    # Extract tokens and POS tags
    if du_dict["pos"]:
        du_dict["pos"] = [
            PosTag(*token_pos_pair.split("/"))
            for token_pos_pair in du_dict["pos"].split()]
    return DialogUtterance(**du_dict)

def generateList(dialog_list):
    for file in range(len(dialog_list)):
        dialog_file=dialog_list[file]
        for i in range(len(dialog_file)):
            attribute_list=[]
            if(dialog_file[i][1]==dialog_file[i-1][1]):
                speaker_change=""
            else:
                speaker_change="SC"
                attribute_list.append(speaker_change)
            if(i==0):
                attribute_list.append("FU")
            tokens_list=dialog_file[i][3].split(" ")
            for token in range(len(tokens_list)):
                attribute_list.append("TOKEN_"+tokens_list[token])
            pos_list=dialog_file[i][2]
            if(pos_list!=None):
                for pos in range(len(pos_list)):
                    attribute_list.append("POS_"+pos_list[pos][1])
            feature_list.append(attribute_list)
            label_list.append(dialog_file[i][0])

def readOutputFile(output_file):
	with open(output_file,"r",encoding="latin1") as fp:
		for line in fp.readlines():
			word=line.rstrip()
			if(len(word)!=0 and (not word.startswith('Filename'))):
				output_file_list.append(word)

def calculate(total_no_labels):
    correct_labels,accuracy=0, 0
    #calculate accuracy
    for i in range(len(label_list)):
        if(label_list[i]==output_file_list[i]):
            correct_labels=correct_labels+1
    if(total_no_labels!=0):
        accuracy=round((correct_labels/total_no_labels)*100,2)
    print("Accuracy: "+str(accuracy)+"%")

feature_list,label_list=[],[] 
output_file_list=[]   
def main():
	dev_dir=sys.argv[1]
	output_file=sys.argv[2]
	dev_dialog_list=list(get_data(sys.argv[1]))
	generateList(dev_dialog_list)
	readOutputFile(output_file)
	total_no_labels=len(label_list)
	calculate(total_no_labels)

if __name__ == '__main__':
    main()