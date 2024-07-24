import pandas as pd
import numpy as np
import pickle

#read data/workid_authorid_institutionid_pubdate24.csv
paper_data = pd.read_csv('data/workid_authorid_institutionid_pubdate24.csv', index_col=0)
# read data/institution_geo24.pkl
with open('data/institution_geo24.pkl', 'rb') as f:
    institution_geo = pickle.load(f)

institution_geo.dropna(subset=['city', 'country_code'], inplace=True)

# filter institutions with valid geo info
paper_data = paper_data[paper_data['institution_id'].isin(institution_geo['institution_id'])]
print('number of ins with valid geo info:', len(paper_data))

# drop all records before 1960
paper_data = paper_data[paper_data['publication_date'] >= '1960-01-01']

paper_data['publication_date'] = pd.to_datetime(paper_data['publication_date'])

print("all records after 1960:", len(paper_data))

# Sort by author_id and publication_date
paper_data.sort_values(by=['author_id', 'publication_date'], inplace=True)

# Calculate the duration of stay in each institution
paper_data['first_publication'] = paper_data.groupby(['author_id', 'institution_id'])['publication_date'].transform('min')
paper_data['last_publication'] = paper_data.groupby(['author_id', 'institution_id'])['publication_date'].transform('max')

# filter the records where the author stay in a ins for less than 2 years
paper_data = paper_data[paper_data['last_publication'] - paper_data['first_publication'] > pd.Timedelta(days=365*2)]
print('filtered paper data length: ', len(paper_data))

# move_data = paper_data.drop_duplicates(subset=['author_id', 'institution_id'], keep='first')
move_data = paper_data.drop(['first_publication', 'last_publication'], axis=1)


move_data['next_work'] = move_data.groupby('author_id')['work_id'].shift(-1)
move_data['next_ins'] = move_data.groupby('author_id')['institution_id'].shift(-1)
# move_data['move_time'] = move_data.groupby('author_id')['publication_date'].shift(-1)
move_data['prev_ins'] = move_data.groupby('author_id')['institution_id'].shift(1)
move_data['prev_work'] = move_data.groupby('author_id')['work_id'].shift(1)
# move_data['prev_ins'] = move_data.groupby('author_id')['institution_id'].shift(1)


# drop records with ins=next_ins and prev_ins != NA (don't drop the first paper of each author)
# move_data = move_data[(move_data['institution_id'] != move_data['next_ins']) | pd.isna(move_data['prev_work'])]

# drop records with ins = prev_ins. In this case, the first paper publicated in the new ins is recorded, 
# the publication date is the move date
move_data = move_data[(move_data['institution_id'] != move_data['prev_ins'])]

print('Number of first paper records', len(move_data))

# drop records with work=next_work or work=prev_work
move_data = move_data[(move_data['work_id'] != move_data['next_work']) \
    & (move_data['work_id'] != move_data['prev_work'])]
print('number of records after handling multiaffiliation: ', len(move_data))

move_data.rename(columns={'publication_date': 'move_time'}, inplace=True)
move_data['leave_time'] = move_data.groupby('author_id')['move_time'].shift(-1)
move_data['stay_time'] = move_data['leave_time'] - move_data['move_time']

# Drop all records with both of prev_ins and leave_time are NA
move_data = move_data[~(pd.isna(move_data['prev_ins']) & pd.isna(move_data['leave_time']))]
print("number of valid movement data (along with the author's first pub:", len(move_data))

# Handle short stay times
move_data = move_data[(move_data['stay_time'] > pd.Timedelta(days=365*2)) | (pd.isna(move_data['stay_time']))]

move_data.loc[:, 'prev_ins'] = move_data.groupby('author_id')['institution_id'].shift(1)

# recalculate stay time
move_data.loc[:, 'leave_time'] = move_data.groupby('author_id')['move_time'].shift(-1)
move_data.loc[:, 'stay_time'] = move_data['leave_time'] - move_data['move_time']

move_data.to_csv('data/move_data.csv')
