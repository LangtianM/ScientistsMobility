import pandas as pd

ccframe = pd.read_csv('data/country-and-continent-codes-list-csv.csv')

def get_continent(country_code):
    
    if country_code == 'XK':
        con = 'EU'
    else:
        con =  str(ccframe.loc[ccframe['Two_Letter_Country_Code'] == country_code ]['Continent_Code'].values[0])
    if(con != 'nan'):
        return con
    else:
        return'NA'
    
# def estimate_this_continent(move_data, continent):

def attr_within_continent(move_data, continent):
    continent_movement = move_data[move_data['continent_code'] == continent]
    countries = continent_movement['country_code'].unique()

    cou_atr = pd.DataFrame(columns=countries)
    print(cou_atr)
    for year in range(1960, 2021, 5):
        slice_data = continent_movement[ (continent_movement['move_year'] >= year)
                                        & (continent_movement['move_year'] < (year+5))]
        cou_atr_slice = dict()
        sum = len(slice_data)
        for country in countries:
            cou_atr_slice[country] = len(slice_data[slice_data['country_code']==country]) / sum
        df_slice = pd.DataFrame([cou_atr_slice], index=['%d-%d'%(year, year+5)])
        cou_atr = pd.concat([cou_atr, df_slice])

    return cou_atr

