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
    for year in range(1960, 2021, 5):
        slice_data = continent_movement[ (continent_movement['move_year'] >= year)
                                        & (continent_movement['move_year'] < (year+5))]
        cou_atr_slice = dict()
        sum = len(slice_data)
        for country in countries:
            cou_atr_slice[country] = len(slice_data[slice_data['country_code']==country]) / sum
        df_slice = pd.DataFrame([cou_atr_slice], index=['%d-%d'%(year, year+5)])
        cou_atr = pd.concat([cou_atr, df_slice])
    sorted_colums = cou_atr.iloc[-1].sort_values(ascending=False).index
    cou_atr = cou_atr[sorted_colums]
    return cou_atr

def attr_within_country(move_data, country):
    country_movement = move_data[move_data['country_code']==country]
    cities = country_movement['city'].unique()
    city_atr = pd.DataFrame(columns=cities)
    for year in range(1960, 2021, 5):
        slice_data = country_movement[(country_movement['move_year'] >= year)
                                    & (country_movement['move_year']<(year+5))]
        city_atr_slice = dict()
        sum = len(slice_data)
        if sum != 0:
            for city in cities:
                city_atr_slice[city] = len(slice_data[
                    slice_data['city'] == city 
                ]) / sum
        else:
            for city in cities:
                city_atr_slice[city] = 0
        df_slice = pd.DataFrame([city_atr_slice], 
                                index=['%d-%d'%(year, year+5)])
        city_atr = pd.concat([city_atr, df_slice])

    sorted_colums = city_atr.iloc[-1].sort_values(ascending=False).index
    city_atr = city_atr[sorted_colums]
    return city_atr

def get_geo_info(institution_id, institution_geo):
    ins_info = institution_geo[institution_geo['institution_id'] == institution_id]
    if ins_info.empty:
        print('Mising Geo Info:', institution_id)
        return {'continent': None, 'country': None, 'city': None}
    return {
        'continent': ins_info['continent_code'].iloc[0],
        'country': ins_info['country_code'].iloc[0],
        'city': ins_info['city'].iloc[0]
    }
    
def level_distance(ins_1, ins_2, institution_geo):
    ins_1_info = get_geo_info(ins_1, institution_geo)
    ins_2_info = get_geo_info(ins_2, institution_geo)
    if ins_1_info['continent'] != ins_2_info['continent']:
        return 3
    elif ins_1_info['country'] != ins_2_info['country']:
        return 2
    elif ins_1_info['city'] != ins_2_info['city']:
        return 1
    else: return 0

