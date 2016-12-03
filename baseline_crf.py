#!/usr/bin/env python3

__author__ = "Sai Geetha Kandepalli Cherukuru"
__email__ = "kandepal@usc.edu"

from collections import namedtuple
import csv
import glob
import os
import sys
import pycrfsuite

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

def generateTestList(test_dir):

    tagger = pycrfsuite.Tagger()
    tagger.open('train-baseline.crfsuite')
    output_file=sys.argv[3]
    fp_w=open(output_file,'w')

    for dirpath, dirs, files in os.walk(test_dir):
        for filename in files:
            if(not filename.startswith('.')):
                fp_w.write(('Filename="'+str(filename)+'"'))
                fp_w.write("\n")
                fname = os.path.join(dirpath, filename)
                dialog_file = get_utterances_from_filename(fname) 
                feature_list=[]  
                for i in range(len(dialog_file)):
                    attribute_list=[]
                    if(dialog_file[i][1]==dialog_file[i-1][1]):
                        speaker_change="0"
                    else:
                        speaker_change="1"
                    if(i==0):
                        attribute_list.append("0")
                    else:
                        attribute_list.append(speaker_change)
                    if(i==0):
                        attribute_list.append("1")
                        speaker_change="0"
                    else:
                        attribute_list.append("0")
                    tokens_list=dialog_file[i][3].split(" ")
                    if(tokens_list!=None):
                        for token in range(len(tokens_list)):
                            attribute_list.append("TOKEN_"+tokens_list[token])
                    else:
                        attribute_list.append("TOKEN_None")
                    pos_list=dialog_file[i][2]
                    if(pos_list!=None):
                        for pos in range(len(pos_list)):
                            attribute_list.append("POS_"+pos_list[pos][1])
                    else:
                        attribute_list.append("POS_None")
                    feature_list.append(attribute_list)
                fp_w.write("\n".join(tagger.tag(feature_list)))
                fp_w.write("\n\n")
    fp_w.close()

def generateList(input_dir):
    feature_list,label_list=[],[]
    for dirpath, dirs, files in os.walk(input_dir):
        for filename in files:
            if(not filename.startswith('.')):
                fname = os.path.join(dirpath, filename)
                dialog_file = get_utterances_from_filename(fname)   
                for i in range(len(dialog_file)):
                    attribute_list=[]
                    if(dialog_file[i][1]==dialog_file[i-1][1]):
                        speaker_change="0"
                    else:
                        speaker_change="1"
                    if(i==0):
                        attribute_list.append("0")
                    else:
                        attribute_list.append(speaker_change)
                    if(i==0):
                        attribute_list.append("1")
                        speaker_change="0"
                    else:
                        attribute_list.append("0")
                    tokens_list=dialog_file[i][3].split(" ")
                    if(tokens_list!=None):
                        for token in range(len(tokens_list)):
                            attribute_list.append("TOKEN_"+tokens_list[token])
                    else:
                        attribute_list.append("TOKEN_None")
                    pos_list=dialog_file[i][2]
                    if(pos_list!=None):
                        for pos in range(len(pos_list)):
                            attribute_list.append("POS_"+pos_list[pos][1])
                    else:
                        attribute_list.append("POS_None")
                    feature_list.append(attribute_list)
                    label_list.append(dialog_file[i][0])
    #print(label_list)
    #print(feature_list)
    return feature_list,label_list

def trainCRF(feature_list,label_list):
    #Train the crfsuite model based on features generated
    trainer = pycrfsuite.Trainer(verbose=False)
    trainer.append(feature_list, label_list)
    trainer.set_params({
        'c1': 1.0,   # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'max_iterations': 100,  # stop earlier

        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    })
    trainer.train('train-baseline.crfsuite')

def main():
    feature_list1,label_list1=generateList(sys.argv[1])
    trainCRF(feature_list1,label_list1)
    generateTestList(sys.argv[2])

if __name__ == '__main__':
    main()