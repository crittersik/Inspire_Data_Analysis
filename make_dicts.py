import json
import os.path
from datetime import datetime
from time import time
import random
import sexmachine.detector as gender

import read_Inspire_data
from data_path import DATA_PATH, DATA_FILE_NAME, FILE_NAMES, FILE_AUTH, \
    FILE_DICT_recid, PATH_recid_bib


##############################
#### Check if there is anything
#### to do at all
if os.path.isfile(DATA_PATH+FILE_NAMES) and os.path.isfile(DATA_PATH+FILE_AUTH) \
        and os.path.isfile(DATA_PATH+FILE_DICT_recid) and os.path.isfile(
                        DATA_PATH+PATH_recid_bib) :
    print 'All files are prepared, nothing more to be done.'
    raise SystemExit


##############################
#### Load data
print 'Ready to load data.'
start = time()
df_clean = read_Inspire_data.load_inspire(DATA_PATH+DATA_FILE_NAME)
# take only sample of rows
#NO_sample = 10000 #1080316 #numer of sample rows taken for analysis
#rows = random.sample(df_clean_aux.index, NO_sample)
#df_clean = df_clean_aux.ix[rows]
end = time()
print 'Data loaded. Time: ', end - start, 's'

##############################
#### Create gender dictionary
def get_gender(name):
    if name in name_memo:
        return name_memo[name]
    else:
        gender = gender_detector.get_gender(name)
        name_memo[name] = gender
        return gender

#create the {name:gender} dictionary and save to .json or load
print 'Ready to prepare name_memo.'
start = time()
if os.path.isfile(DATA_PATH+FILE_NAMES) and not os.path.isfile(DATA_PATH+FILE_AUTH):
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
end = time()
print 'name_memo done. Time: ', end - start, 's'

##############################
#### Create recid dictionary
#### with citations
print 'Ready to prepare recid dictionary with citations.'
start = time()

# add 5 year citation count, define # of months
Nmonths = 60


if not os.path.isfile(DATA_PATH+FILE_DICT_recid):
    # create a dict with dates per recid
    recid_dict = {}
    for row in  df_clean.iterrows():
        row_num, actual_row = row
        recid_dict[actual_row['recid']] = {}
        recid_dict[actual_row['recid']]['date'] = actual_row['date'].strftime('%Y-%m-%d')

    # add total citation and 5-year citation count to the dictionary
    for row in  df_clean.iterrows():
        row_num, actual_row = row
        paper_date = actual_row['date']
        recid_dict[actual_row['recid']]['cit_5'] = 0
        recid_dict[actual_row['recid']]['cit_tot'] = actual_row['cit_count']
        recid_dict[actual_row['recid']]['cit_list'] = actual_row['citations']
        for cpaper in actual_row['citations']:
            if cpaper in recid_dict:
                citation_date = datetime.strptime(recid_dict[cpaper]['date'], '%Y-%m-%d')
                if 0 < (citation_date - paper_date).days/30 < Nmonths:
                    recid_dict[actual_row['recid']]['cit_5'] += 1

    with open(DATA_PATH + FILE_DICT_recid, "wb") as outfile:
        for key, value in recid_dict.items():
            outfile.write(json.dumps([key, value]) + "\n",)
else:
    recid_dict = {}
    with open(DATA_PATH+FILE_DICT_recid) as infile:
        for line in infile:
            key, value = json.loads(line)
            recid_dict[key] = value

end = time()
print 'Recid dictionary done. Time: ', end - start, 's'


##############################
#### Create recid dictionary
#### with  bibliography
print 'Ready to prepare recid dictionary with bibliography.'
start = time()

# add function that takes a recid to citation list dictionary, list of
# recid's and a date, and filters the list of papers taking only papers
# published earlier that the origin date
def date_filter_citations(recid_citation, cit_list, date_origin):
    earlier_recids_aux = [elem for elem in cit_list
                 if elem in recid_citation]
    earlier_recids = [elem for elem in earlier_recids_aux
                 if datetime.strptime(recid_citation[elem]['date'], "%Y-%m-%d") < date_origin]
    return len(earlier_recids)

# Now we prepare the function that will take average citation count of a
# given list of papers by recid
# only inlcude citations before a given year

def average_cit_count_date(recid_citation, recid_list, date_origin):
    citations = [ date_filter_citations(recid_citation, recid_citation[elem][
        'cit_list'], date_origin) for elem in recid_list
                 if elem in recid_citation ]
    if len(citations)==0:
        return 0
    return float(sum(citations))/len(citations)

    # add bibliography and average citation of referenced papers, at the date
    #  of publication
if not os.path.isfile(DATA_PATH+PATH_recid_bib):
    recid_bib = {}
    for row in  df_clean.iterrows():
        row_num, actual_row = row
        paper_date = actual_row['date']
        recid_bib[actual_row['recid']] = {}

        recid_bib[actual_row['recid']]['bib'] = actual_row['references']
        recid_bib[actual_row['recid']]['bib_av_cit'] = \
            average_cit_count_date(recid_dict, actual_row['references'],
                                   actual_row['date'])

    with open(DATA_PATH + PATH_recid_bib, "wb") as outfile:
        for key, value in recid_bib.items():
            outfile.write(json.dumps([key, value]) + "\n",)

end = time()
print 'Recid to bib dictionary done. Time: ', end - start, 's'


##############################
#### Create authors dictionary
print 'Ready to prepare authors dictionary.'
start = time()

def get_name(author):
    name = author.split(", ")[-1].split(" ")[0]

def average_cit_count(recid_list):
    citations = [recid_dict[elem]['cit_tot'] for elem in recid_list if elem in recid_dict]
    if len(citations)==0:
        return 0
    return float(sum(citations))/len(citations)

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

    for auth in authors.keys():
        authors[auth]['av_cit'] = average_cit_count(authors[auth]['papers'])

    with open(DATA_PATH + FILE_AUTH, "wb") as outfile:
        for key, value in authors.items():
            outfile.write(json.dumps([key, value]) + "\n",)

end = time()
print 'Authors dictionary done. Time: ', end - start, 's'
