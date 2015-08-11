import json
import os.path
import sys

from datetime import datetime
from time import time

import pandas as pd
import numpy as np
import random
import math
import types
import csv
#import time

import sexmachine.detector as gender


import read_Inspire_data
from data_path import DATA_PATH, DATA_FILE_NAME

FILE_NAMES = "name_memo.json"
FILE_AUTH = "authors.json"
FILE_DICT_recid = "recid_dict.json"

##############################
#### Check if there is anything
#### to do at all
if os.path.isfile(DATA_PATH+FILE_NAMES) and os.path.isfile(DATA_PATH+FILE_AUTH) \
        and os.path.isfile(DATA_PATH+FILE_DICT_recid):
    raise SystemExit


##############################
#### Load data
df_clean = read_Inspire_data.load_inspire(DATA_PATH+DATA_FILE_NAME)


##############################
#### Create gender dictionary
def get_gender(name):
    if name in name_memo:
        return name_memo[name]
    else:
        gender = gender_detector.get_gender(name)
        name_memo[name] = gender
        return gender

#create the name-gender dictionary and save to .json or load
if os.path.isfile(DATA_PATH+FILE_NAMES):
    name_memo = {}
    with open(DATA_PATH+FILE_NAMES) as infile:
        for line in infile:
            key, value = json.loads(line)
            name_memo[key] = value
else:
    # Initialize Gender Detector
    gender_detector = gender.Detector(case_sensitive=False)

    #create a dictionary
    name_memo = {}
    for row in df_clean.iterrows():
        row_num, actual_row = row
        auth_list = actual_row['tot_auth_list']
        for single_author in auth_list:
            name = single_author.split(", ")[-1].split(" ")[0]
            get_gender(name.lower())

    #save modified names dictionary to file
    with open(DATA_PATH + FILE_NAMES, "wb") as outfile:
        for key, value in name_memo.items():
            outfile.write(json.dumps([key, value]) + "\n",)


##############################
#### Create authors dictionary
def get_name(author):
    name = author.split(", ")[-1].split(" ")[0]

authors = {}
if not os.path.isfile(DATA_PATH+FILE_AUTH):
    for row in df_clean.iterrows():
        row_num, actual_row = row
        auth_list = actual_row['tot_auth_list']
        paper = str(actual_row['recid'])

        if type(auth_list) is list:
            #convert to lowercase to collect only unique names
            auth_list = [author.lower() for author in auth_list]

            for author in auth_list:
                #search if author_year has already been seen
                if not author in authors :
                    authors[author] = {}
                    name = str(get_name(author))
                    authors[author]['gender'] = name_memo[name] if name in name_memo else 'andy'
                    authors[author]['papers'] = []
                    #authors[author]['collaborators'] = []

                authors[author]['papers'] = authors[author]['papers'] + [int(paper)]
                #authors[author]['collaborators'] = authors[author]['collaborators'] + auth_list

    with open(DATA_PATH + FILE_AUTH, "wb") as outfile:
        for key, value in authors.items():
            outfile.write(json.dumps([key, value]) + "\n",)


##############################
#### Create recid dictionary

# add 5 year citation count
Nmonths = 60

if not os.path.isfile(DATA_PATH+FILE_DICT_recid):
    #create a dict with dates per recid
    recid_dict = {}
    for row in  df_clean.iterrows():
        row_num, actual_row = row
        recid_dict[actual_row['recid']] = {}
        recid_dict[actual_row['recid']]['date'] = actual_row['date'].strftime('%Y-%m-%d')

    #add total citation and 5-year citation count to the dictionary
    for row in  df_clean.iterrows():
        row_num, actual_row = row
        paper_date = actual_row['date']
        recid_dict[actual_row['recid']]['cit_5'] = 0
        recid_dict[actual_row['recid']]['cit_tot'] = actual_row['cit_count']
        for cpaper in actual_row['citations']:
            if cpaper in recid_dict:
                citation_date = datetime.strptime(recid_dict[cpaper]['date'], '%Y-%m-%d')
                if 0 < (citation_date - paper_date).days/30 < Nmonths:
                    recid_dict[actual_row['recid']]['cit_5'] += 1

    with open(DATA_PATH + FILE_DICT_recid, "wb") as outfile:
        for key, value in recid_dict.items():
            outfile.write(json.dumps([key, value]) + "\n",)