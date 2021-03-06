## High Energy Physics (HEP) Publication Data Analysis

Based on the data from InspireHEP I perform some simple statistical analysis, being interested how factors such as citation count, paper count, number of collaborators vary in time and with sex of the author.

InspireHEP is a High-Energy Physics Literature Database. The data are available here: 
http://inspirehep.net/info/hep/api

To download and unpack the data file use download_data.py:
python download_data.py 

To set destination path and also some of the filenames, use data_path.py.

The file read_Inspire_data.py contains a function that reads the JSON data and creates a pandas dataframe.
It is used by all the notebooks. Some very basic overview of the data is in Inspire_basic_plots.ipynb
You can also view this basic plots notebook with ipython notebook viewer:
http://nbviewer.ipython.org/github/crittersik/Inspire_Data_Analysis/blob/master/Inspire_basic_plots.ipynb

In Inspire_predict_citations.ipynb I am doing some simple feature engineering and machine learning on the data to predict citations count. 
I is stil pretty raw, we'll add some more work, better model validation later. To run this notebook with all possible features, you should at first compile
make_dicts.py . Watch out, computing dict_bib.json in the present form takes 20 hours.