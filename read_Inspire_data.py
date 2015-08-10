import pandas as pd
import json
from datetime import datetime


def try_parsing_date(text):
    if text is None:
        return 'NaN'
    for fmt in ("%Y-%m-%d",  "%Y-%m", "%Y-%B", "%Y-%b.", "%Y-%b", "%b %Y", '%Y',"%Y,%m,%d" ,"%Y/%m/%d","%Y/%m", "%B %Y", "%b. %Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return 'NaN'

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

    df['date'] = map(try_parsing_date, df['creation_date'])
    df['year'] = map(lambda x: x.year, df['date'])

    df_temp = df[df['date'] != 'NaN']


# choose to return only relevant features for further analysis
    return df_temp[['abstract','citations', 'free_keywords', 'recid',
                     'references', 'standardized_keywords', 'title',
                     'tot_auth_count', 'tot_auth_list', 'cit_count',
                     'free_kwd_count', 'std_kwd_count', 'ref_count',
                     'title_len', 'abstract_len', 'date', 'year']]



