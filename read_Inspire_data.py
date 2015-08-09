import pandas as pd
import json
import numpy as np
import sys

DATA_PATH = "/inspire_data/records-2015-03-04" \
			".json"
#take path
if len(sys.argv) > 1:
	DATA_PATH = sys.argv[1]


def make_date(string_date):
    if string_date is None:
        return 0
    try:
        return int(string_date[:4])
    except:
        return 0

def load_inspire(path):
	columns = {}
	with open(path, "rb") as plik:
		for line in plik:
			record = json.loads(line)
			for key, value in record.items():
				columns.setdefault(key, []).append(value)
				
	df = pd.DataFrame(data=columns)
	df['coauth_count'] = map(len, df['co-authors'])
	df['authors_count'] = map(len, df['authors'])
	df['tot_auth_count'] = df.authors_count + df.coauth_count
	df['tot_auth_list'] = df['authors'] + df['co-authors']
	df['cit_count'] = map(len, df['citations'])
	df['free_kwd_count'] = map(len, df['free_keywords'])
	df['std_kwd_count'] = map(len, df['standardized_keywords'])
	df['ref_count'] = map(len, df['references'])
	df['title_len'] = map(len, df['title'])
	df['abstract_len'] = map(len, df['abstract'])
	df['year'] = map(make_date, df['creation_date'])

	df_temp = df[(df['coauth_count'] + df['authors_count'] > 0)]
	df_clean = df_temp[df_temp['year'] >= 1910]
	return df
	
if __name__ == "__main__":
	df = load_inspire(DATA_PATH)

