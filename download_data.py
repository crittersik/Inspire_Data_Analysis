import gzip
import glob
import os.path
import urllib
import sys

URL = "http://inspirehep.net/hep_records.json.gz"
FILE_NAME = "hep_records.json.gz"

# take path
if len(sys.argv) > 1:
	PATH = sys.argv[1]

# download file
if not os.path.isfile(PATH+FILE_NAME):
    testfile = urllib.URLopener()
    testfile.retrieve(URL, PATH+FILE_NAME)

# unpack file
if not os.path.isfile(PATH+FILE_NAME[:-3]):
    for src_name in glob.glob(os.path.join(PATH, '*.gz')):
        base = os.path.basename(src_name)
        dest_name = os.path.join(PATH, base[:-3])
        with gzip.open(src_name, 'rb') as infile:
            with open(dest_name, 'w') as outfile:
                for line in infile:
                    outfile.write(line)