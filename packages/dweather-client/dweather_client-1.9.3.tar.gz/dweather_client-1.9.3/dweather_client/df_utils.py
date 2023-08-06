"""
Helpful auxilliary functions that don't directly interact with IPFS.
Basically, it should go here if it doesn't need to import from df_loader or http_client,
this module uses pandas
"""
import math
import pandas as pd
import numpy as np
import datetime
import os

PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
CPC_LOOKUP_PATH = PARENT_DIR + '/etc/cpc-grid-ids.csv'
ICAO_LOOKUP_PATH = PARENT_DIR + '/etc/airport-codes.csv'

def dataframeify(dict_or_df):
    """
    Convert a dict to a dataframe.
    If "dict" is already a dataframe, just return it.
    """
    if isinstance(dict_or_df, pd.DataFrame):
        return dict_or_df
    else:
        return pd.DataFrame.from_dict(dict_or_df, orient="index")


def cpc_grid_to_lat_lon(grid):
    """ 
    Convert a cpc grid id to conventional lat lon via a lookup table.
    return:
        latitude, longitude
        
    args:
        grid = "1100" example
    
    """
    cpc_grids =  pd.read_csv(os.path.join(CPC_LOOKUP_PATH)).set_index('Grid ID') #dataframe of cpc grid to lat/lon lookup table
    myGrid = cpc_grids.iloc[grid]
    coords = [myGrid["Latitude"], myGrid["Longitude"]]
    coords = [coord+360 if coord < 0 else coord for coord in coords] #converts negative coordinates to positive values
    
    return coords[0], coords[1]


def get_station_ids_with_icao():
    """
    Get a list of station id that are associated with stations that have an icao code.
    """
    icao_lookup = pd.read_csv(os.path.join(ICAO_LOOKUP_PATH)).set_index('ICAO')
    ids = []
    for index, row in icao_lookup.iterrows():
        if (row["GHCN"] not in ids):
            ids.append(row["GHCN"])
    return ids

def icao_to_ghcn(icao):
    """ 
    Convert an icao airport code to ghcn.
    return:
        latitude, longitude
    args:
        icao = "xxxx" for example try "KLGA"
    """
    icao_codes = pd.read_csv(os.path.join(ICAO_LOOKUP_PATH)).set_index('ICAO') #get lookup table
    return icao_codes.loc[icao]["GHCN"]


def period_slice_df(df, ps, pe, yrs):
    """ 
    Slice a dataframe by period where n is based on years lookback 
    
    return:
        pd.DataFrame()
    
    args:
        df = any pd.DataFrame() with a datetime.date() index
        ps = datetime.date object (contract period start)
        ps = datetime.date object (contract period end)
        yrs = 30 (years lookback)
        
    limitations:
        max period is 364 days
        
    """

    mydf = pd.DataFrame()
    
    leftDay = ~((df.index.day < ps.day) & (df.index.month == ps.month))
    rightDay = ~((df.index.day > pe.day) & (df.index.month == pe.month))
    #first year just get end
    if ps.year < pe.year:
        firstYear = ps.year - yrs
        yr = df.index.year == firstYear
        mon = df.index.month >= ps.month
        #a boolean mask to cut the left and right half month days if need be
        mydf = mydf.append(df[(yr)&(mon)&(leftDay)])
        #everything in betweeng
        for yrss in range(ps.year - (yrs - 1), pe.year - 1):
            ##boolean mask for now, better method needed##
            yearChunk = (df.index.year == yrss)&((df.index.month<=pe.month)|(df.index.month>=ps.month))
            yearChunk = (yearChunk)&leftDay&rightDay
            mydf = mydf.append(df[yearChunk])
        #build last year
        mydf = mydf.append(df[rightDay&(df.index.month<=pe.month)&(df.index.year==pe.year-1)])
    else:
        mydf = df[leftDay&rightDay&(df.index.month>=ps.month)&(df.index.month<=pe.month)&(df.index.year>=ps.year-yrs)]
            
    return mydf

def boxed_storms(df, min_lat, min_lon, max_lat, max_lon):
    return df[(df['lat'] >= min_lat) & (df['lon'] >= min_lon) & (df['lat'] <= max_lat) & (df['lon'] <= max_lon)]

def nearby_storms(df, c_lat, c_lon, radius): 
    """
    return:
        DataFrame with all time series points in `df` within `radius` in km of the point `(c_lat, c_lon)`

    args:
        c_lat (float): latitude coordinate of bounding circle
        c_lon (float): longitude coordinate of bounding circle
    """ 
    dist = haversine_vectorize(df['lon'], df['lat'], c_lon, c_lat)
    return df[dist < radius]

def haversine_vectorize(lon1, lat1, lon2, lat2):
    """
    Vectorized version of haversine great circle calculation. 
    return: 
        distance in km between `(lat1, lon1)` and `(lat2, lon2)`

    args:
        lon1 (float) first longitude coord
        lat1 (float) first latitude coord
        lon2 (float) second longitude coord
        lat2 (float) second latitude coord
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    newlon = lon2 - lon1
    newlat = lat2 - lat1
    haver_formula = np.sin(newlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon/2.0)**2
    dist = 2 * np.arcsin(np.sqrt(haver_formula))
    km = 6367 * dist
    return km
