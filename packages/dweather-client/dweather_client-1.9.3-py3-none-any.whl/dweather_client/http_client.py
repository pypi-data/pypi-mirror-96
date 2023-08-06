"""
Basic functions for getting data from a dWeather gateway via https.
"""
import os, pickle, math, requests, datetime, io, gzip, json, logging, csv, tarfile
from dweather_client.ipfs_errors import *
from dweather_client.utils import listify_period, lat_lon_to_rtma_grid, find_closest_lat_lon, build_rtma_reverse_lookup, build_rtma_lookup, conventional_lat_lon_to_cpc, cpc_lat_lon_to_conventional, mms_to_inches, celcius_to_fahrenheit
import dweather_client.ipfs_datasets
from collections import Counter, deque

MM_TO_INCHES = 0.0393701
RAINFALL_PRECISION = 5
GATEWAY_URL = 'https://gateway.arbolmarket.com'

def get_heads(url=GATEWAY_URL):
    """
    Get heads.json for a given IPFS gateway.
    Args:
        url (str): base url of the IPFS gateway url
    Returns (example heads.json):
        {
            'chirps_05-daily': 'Qm...',
            'chirps_05-monthly': 'Qm...',
            'chirps_25-daily': 'Qm...',
            'chirps_25-monthly': 'Qm...',
            'cpc_us-daily': 'Qm...',
            'cpc_us-monthly': 'Qm...'
        }
    """
    hashes_url = url + "/climate/hashes/heads.json"
    r = requests.get(hashes_url)
    r.raise_for_status()
    return r.json()

def get_metadata(hash_str, url=GATEWAY_URL):
    """
    Get the metadata file for a given hash.
    Args:
        url (str): the url of the IPFS server
        hash_str (str): the hash of the ipfs dataset
    Returns (example metadata.json):
    
        {
            'date range': [
                '1981/01/01',
                '2019/07/31'
            ],
            'entry delimiter': ',',
            'latitude range': [
                -49.975, 49.975
            ],
            'longitude range': [
                -179.975, 179.975]
            ,
            'name': 'CHIRPS .05 Daily Full Set Uncompressed',
            'period': 'daily',
            'precision': 0.01,
            'resolution': 0.05,
            'unit of measurement': 'mm',
            'year delimiter': '\n'
        }
    """
    metadata_url = "%s/ipfs/%s/metadata.json" % (url, hash_str)
    r = requests.get(metadata_url)
    r.raise_for_status()
    return r.json()

def traverse_ll(head):
    release_itr = head
    release_ll = deque()
    while True:
        release_ll.appendleft(release_itr)
        prev_release = get_metadata(release_itr)['previous hash']
        if prev_release != None:
            release_itr = prev_release
        else:
            return release_ll

def get_hurricane_release_dict(release_hash, url=GATEWAY_URL):
    url = "%s/ipfs/%s/history.json.gz" % (url, release_hash)
    resp = requests.get(url)
    resp.raise_for_status()
    with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as zip_data:
        return json.loads(zip_data.read().decode("utf-8"))

def get_hurricane_dict(head=get_heads()['atcf_btk-seasonal']):
    """
    Get a hurricane dictionary for the atcf_btk-seasonal dataset. 

    To get a unique value to query the dict by storm, use BASIN + CY + the year
    part of the HOUR value. BASIN is the ocean, CY is the storm index, and
    the year is needed as well because the storm index resets every year.

    Note that there will be multiple readings with the same HOUR value,
    as readings are taken more than once per hour and then rounded to the nearest
    hour before posting. 
    """
    heads = get_heads()
    hurr_head = heads['atcf_btk-seasonal']
    release_ll = traverse_ll(hurr_head)
    hurr_dict = {}
    for release_hash in release_ll:
        release_content = get_hurricane_release_dict(release_hash)
        try:
            hurr_dict['features'] += release_content['features']
        except KeyError:
            hurr_dict.update(release_content)
    return hurr_dict

def get_simulated_hurricane_files(basin):
    """
    Gets the names of files containing STORM simulated TC data. Takes a basin ID, one of:
    EP, NA, NI, SI, SP or WP
    """
    if basin not in {'EP', 'NA', 'NI', 'SI', 'SP', 'WP'}:
        raise ValueError("Invalid basin ID")
    heads = get_heads()
    hurr_hash = heads['storm-simulated-hurricane']
    metadata  = get_metadata(hurr_hash)
    base_url = f"{GATEWAY_URL}/ipfs/{hurr_hash}/"
    files = [base_url + f for f in metadata['files'] if basin in f]
    return files

def get_ibracs_hurricane_file():
    heads = get_heads()
    hurr_hash = heads['ibtracs-tropical-storm']
    metadata = get_metadata(hurr_hash)
    base_url = f"{GATEWAY_URL}/ipfs/{hurr_hash}/"
    return base_url + metadata["files"][0]

def get_station_csv(station_id, station_dataset="ghcnd-imputed-daily", url=GATEWAY_URL):
    """
    Retrieve the contents of a station data csv file.
    Args:
        station_id (str): the id of the weather station
        station_dataset (str): which dataset to use, on of ["ghcnd", "ghcnd-imputed-daily"]
    returns:
        the contents of the station csv file as a string
    """
    all_hashes = get_heads()
    dataset_hash = all_hashes[station_dataset]
    dataset_url = "%s/ipfs/%s/%s.csv.gz" % (url, dataset_hash, str(station_id))
    r = requests.get(dataset_url)
    r.raise_for_status()
    with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as zip_data:
        return zip_data.read().decode("utf-8")


def parse_station_snow_depth_as_dict(csv_text, use_inches=True):
    return parse_station_snow_as_dict( \
        csv_text, 
        snow_representation="SNWD",
        use_inches=True
    )

def parse_station_snowfall_as_dict(csv_text, use_inches=True):
    return parse_station_snow_as_dict( \
        csv_text,
        snow_representation="SNOW",
        use_inches=True
    )


def parse_station_snow_as_dict(csv_text, snow_representation, use_inches=True):
    reader = csv.reader(csv_text.split())
    column_names = next(reader)
    date_col = column_names.index('DATE')
    snow_col = column_names.index(snow_representation)
    snowfall = {}
    for row in reader:
        if row[snow_col] == '':
            continue
        row_snow = float(row[snow_col])/10.0
        if use_inches:
            row_snow = mms_to_inches(row_snow)
        snowfall[datetime.datetime.strptime(row[date_col], "%Y-%m-%d").date()] = row_snow
    return snowfall

def parse_station_temps_as_dict(csv_text, use_fahrenheit=True):
    """
    Parse a station CSV file and get column values
    Will automatically index by date
    Args:
        csv_text (str): the GHCND station csv text
        use_fahrenheight (bool): if true use deg F, otherwise degrees C
    Returns:
        tuple:
            dict of datetime.date: float temperature highs
            dict of datetime.date: float temperature lows
    """
    reader = csv.reader(csv_text.split())
    column_names = next(reader)
    date_col = column_names.index('DATE')
    tmax_col = column_names.index('TMAX')
    tmin_col = column_names.index('TMIN')
    tmins = {}
    tmaxs = {}
    for row in reader:
        # data is in tenths of a degree C
        if row[tmin_col] == '' or row[tmax_col] == '':
            continue
        tmax = float(row[tmax_col])/10.0
        tmin = float(row[tmin_col])/10.0
        if use_fahrenheit:
            tmax = celcius_to_fahrenheit(tmax)
            tmin = celcius_to_fahrenheit(tmin)
        tmaxs[datetime.datetime.strptime(row[date_col], "%Y-%m-%d").date()] = tmax
        tmins[datetime.datetime.strptime(row[date_col], "%Y-%m-%d").date()] = tmin

    return tmins, tmaxs

def get_station_by_wmo_id(wmo_id):
    pass

def get_station_by_airport_code(code):
    pass

def get_hash_cell(hash_str, coord_str, url=GATEWAY_URL):
    dataset_url = '%s/ipfs/%s/%s' % (url, hash_str, coord_str)
    r = requests.get(dataset_url)
    r.raise_for_status()
    return r.text

def get_zipped_hash_cell(hash_str, coord_str, url=GATEWAY_URL):
    """
    Read a text file on the ipfs server compressed with gzip.
    Args:
        url (str): the url of the ipfs server
        hash_str (str): the hash of the dataset
        coord_str (str): the text file coordinate name e.g. 45.000_-96.000
    Returns:
        the contents of the file as a string
    """
    dataset_url = '%s/ipfs/%s/%s.gz' % (url, hash_str, coord_str)
    r = requests.get(dataset_url)
    r.raise_for_status()
    with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as zip_data:
        return zip_data.read().decode("utf-8")

class RTMAClient:
    def __init__(self):
        logging.info("Loading rtma valid lat lons")
        with gzip.GzipFile(os.path.join(os.path.dirname(__file__), 'etc/rtma_lat_lons.p.gz')) as lat_lons:
            self.valid_lat_lons = pickle.load(lat_lons)
        self.rtma_head = get_heads()['rtma_pcp-hourly']
        self.metadata = get_metadata(self.rtma_head)
        self.rtma_start_date = datetime.datetime.strptime(self.metadata['date range'][0], "%Y-%m-%dT%H:%M:%S")
        self.rtma_end_date = datetime.datetime.strptime(self.metadata['date range'][1], "%Y-%m-%dT%H:%M:%S")
        logging.info("Downloading rtma grid lookup")
        r = requests.get('%s/ipfs/%s/grid_history.txt.gz' % (GATEWAY_URL, self.rtma_head))
        r.raise_for_status()
        logging.info("Unzipping rtma grid lookup")
        with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as grid_history_file:
            grid_history = grid_history_file.read().decode('utf-8')
        logging.info("Loading rtma grid lookup")
        self.r_lookup = build_rtma_reverse_lookup(grid_history)
        self.new_grid = list(self.r_lookup.keys())[-1]

    def get_best_rtma_dict(self, lat, lon):
        lat, lon = float(lat), float(lon)
        lat, lon = conventional_lat_lon_to_cpc(lat, lon)
        if ((lat < 20) or (53 < lat)):
            raise InputOutOfRangeError('RTMA only covers latitudes 20 thru 53')
        if ((lon < 228) or (300 < lon)):
            raise InputOutOfRangeError('RTMA only covers longitudes -132 thru -60')
        lat, lon = str(lat), str(lon)
        logging.info('Finding closest lat lon')
        logging.info('Number of buckets in lookup: %i' % len(self.valid_lat_lons))
        closest_lat_lon = find_closest_lat_lon(self.valid_lat_lons[(lat[:2], lon[:3])], (lat, lon))
        logging.info('Finding rtma xy associated with closest lat lon')
        lat_xy = self.r_lookup[self.new_grid]['lat'][closest_lat_lon[0]]
        lon_xy = self.r_lookup[self.new_grid]['lon'][closest_lat_lon[1]]
        assert lat_xy == lon_xy
        return cpc_lat_lon_to_conventional(closest_lat_lon[0], closest_lat_lon[1]), self.get_rtma_dict(lat_xy[0], lat_xy[1])

    def get_rtma_dict(self, x, y):
        r = requests.get('%s/ipfs/%s/%s_%s.gz' % (GATEWAY_URL, self.rtma_head, str(x).zfill(4), str(y).zfill(4)))
        r.raise_for_status()
        with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as cell_text_file:
            cell_text = cell_text_file.read().decode('utf-8')
        hour_itr = self.rtma_start_date
        rtma_dict = {}
        for year_data in cell_text.split('\n'):
            for hour_data in year_data.split(','):
                rtma_dict[hour_itr] = hour_data
                hour_itr = hour_itr + datetime.timedelta(hours=1)
        assert hour_itr == self.rtma_end_date
        return rtma_dict

def get_full_rtma_history(lat, lon):
    """
    Calls endpoint that iterates through all updates to the RTMA dataset and returns a dictionary
    containing the full time series of data.
    Args:
        lat (float): latitude coordinate of RTMA data
        lon (float): longitude coordinate of RTMA data
    Returns:
        tuple containing (<ret_lat>, <ret_lon>, <data>)
        where ret_lat and ret_lon are floats representing the coordinates of the data after the
        argument coordinates are snapped to the RTMA grid, and <data> is a time series dict with 
        datetime keys
    """
    if ((lat < 20) or (53 < lat)):
        raise InputOutOfRangeError('RTMA only covers latitudes 20 thru 53')
    if ((lon < -132) or (-60 < lon)):
        raise InputOutOfRangeError('RTMA only covers longitudes -132 thru -60')
    base_url = "https://parser.arbolmarket.com/linked-list/rtma"
    r = requests.get(f"{base_url}/{lat}_{lon}")
    resp = r.json()
    data_dict = {}
    for k, v in resp["data"].items():
        data_dict[datetime.datetime.fromisoformat(k)] = v
    return ((resp["lat"], resp["lon"]), data_dict)

def get_dataset_cell(lat, lon, dataset_revision):
    """ 
    Retrieve the text of a grid cell data file for a given lat lon and dataset.
    Args:
        lat (float): the latitude of the grid cell, to 3 decimals
        lon (float): the longitude of the grid cell, to 3 decimals
    Returns:
        A tuple (json, str) of the dataset metadata file and the grid cell data text
    Raises: 
        DatasetError: If no matching dataset found on server
        InputOutOfRangeError: If the lat/lon is outside the dataset range in metadata
        CoordinateNotFoundError: If the lat/lon coordinate is not found on server
    """
    all_hashes = get_heads()
    if dataset_revision in all_hashes:
        dataset_hash = all_hashes[dataset_revision]
    else:
        raise DatasetError('{} not found on server'.format(dataset_revision))

    metadata = get_metadata(dataset_hash)
    min_lat, max_lat = sorted(metadata["latitude range"])
    min_lon, max_lon = sorted(metadata["longitude range"])
    if lat < min_lat or lat > max_lat:
        raise InputOutOfRangeError("Latitude {} out of dataset revision range [{:.3f}, {:.3f}] for {}".format(lat, min_lat, max_lat, dataset_revision))
    if  lon < min_lon or lon > max_lon:
        raise InputOutOfRangeError("Longitude {} out of dataset revision range [{:.3f}, {:.3f}] for {}".format(lon, min_lon, max_lon, dataset_revision))
    coord_str = "{:.3f}_{:.3f}".format(lat,lon)
    try:
        if "compression" in metadata and metadata["compression"] == "gzip":
            text_data = get_zipped_hash_cell(dataset_hash, coord_str)
        else:
            text_data = get_hash_cell(dataset_hash, coord_str)
        return metadata, text_data
    except requests.exceptions.RequestException as e:
        raise CoordinateNotFoundError('Coordinate ({}, {}) not found  on ipfs in dataset revision {}'.format(lat, lon, dataset_revision))

def get_rainfall_dict(lat, lon, dataset_revision, return_metadata=False, get_counter=False):
    """ 
    Build a dict of rainfall data for a given grid cell.
    Args:
        lat (float): the latitude of the grid cell, to 3 decimals
        lon (float): the longitude of the grid cell, to 3 decimals
    Returns:
        a dict ({datetime.date: float}) of datetime dates and the corresponding rainfall in mm for that date
    Raises:
        DatasetError: If no matching dataset found on server
        InputOutOfRangeError: If the lat/lon is outside the dataset range in metadata
        CoordinateNotFoundError: If the lat/lon coordinate is not found on server
        DataMalformedError: If the grid cell file can't be parsed as rainfall data
    """
    metadata, rainfall_text = get_dataset_cell(lat, lon, dataset_revision)
    dataset_start_date = datetime.datetime.strptime(metadata['date range'][0], "%Y/%m/%d").date()
    dataset_end_date = datetime.datetime.strptime(metadata['date range'][1], "%Y/%m/%d").date()
    timedelta = dataset_end_date - dataset_start_date
    days_in_record = timedelta.days + 1 # we have both the start and end date in the dataset so its the difference + 1
    day_strs = rainfall_text.replace(',', ' ').split()
    if (len(day_strs) != days_in_record):
        raise DataMalformedError ("Number of days in data file does not match the provided metadata")
    rainfall_dict = Counter({}) if get_counter else {}
    for i in range(days_in_record):
        if day_strs[i] == metadata["missing value"]:
            rainfall_dict[dataset_start_date + datetime.timedelta(days=i)] = 0 if get_counter else None
        else:
            rainfall_dict[dataset_start_date + datetime.timedelta(days=i)] = float(day_strs[i])
    if return_metadata:
        return metadata, rainfall_dict
    else:
        return rainfall_dict


def get_prismc_dict(lat, lon, dataset):
    """
    Builds a dict of latest PRISM data by using datasets combining all PRISM revisions
    Args:
        lat (float): the latitude of the grid cell, to 3 decimals
        lon (float): the longitude of the grid cell, to 3 decimals
        dataset (str): one of 'precip', 'tmax' or 'tmin'
    Returns:
        a dict ({datetime.date: float}) of datetime dates and the corresponding weather values.
        Units are mm for precip or degrees F for tmax and tmin
    """
    if dataset not in {"precip", "tmax", "tmin"}:
        raise ValueError("Dataset must be 'precip', 'tmax' or 'tmin'")
    str_lat, str_lon = "{:.3f}".format(lat), "{:.3f}".format(lon)
    prismc_head = get_heads()[f"prismc-{dataset}-daily"]
    date_dict = {}
    hashes = traverse_ll(prismc_head)
    for h in list(hashes)[::-1]:
        tar_url = f"{GATEWAY_URL}/ipfs/{h}/{str_lat}.tar"
        resp = requests.get(tar_url)
        resp.raise_for_status()
        with tarfile.open(fileobj=io.BytesIO(resp.content)) as tar:
            with tar.extractfile(f"{str_lat}_{str_lon}.gz") as f:
                with gzip.open(f) as gz:
                    for i, line in enumerate(gz):
                        day_of_year = datetime.date(1981 + i, 1, 1)
                        data_list = line.decode('utf-8').strip().split(',')
                        for point in data_list:
                            if (day_of_year not in date_dict) and point:
                                date_dict[day_of_year] = float(point)
                                day_of_year += datetime.timedelta(days=1)
    return date_dict

def get_rev_rainfall_dict(lat, lon, dataset, desired_end_date, latest_rev):
    """
    Build a dictionary of rainfall data. Include as much of the most accurate, final data as possible. Start by buidling from the most accurate data,
    then keep appending data from more recent/less accurate versions of the dataset until we run out or reach the end date.

    This will not throw an error if there are no revisions with data available, it will simply return what is available.
    Args:
        lat (float): the grid cell latitude
        lon (float): the grid cell longitude
        dataset (str): the name of the dataset, e.g., "chirps_05-daily" on hashes.json
        desired_end_date (datetime.date): the last day of data needed.
        latest_rev (str): the least accurate revision of the dataset that is considered final
    Returns:
        tuple:
            a dict ({datetime.date: float}) of datetime dates and the corresponding rainfall in mm for that date
            bool is_final: if all data up to desired end date is final, this will be true
    """
    all_rainfall = {}
    is_final = True

    # Build the rainfall from the most accurate revision of the dataset to the least
    for dataset_revision in dweather_client.ipfs_datasets.datasets[dataset]:
        additional_rainfall = get_rainfall_dict(lat, lon, dataset_revision)
        all_dates = list(all_rainfall) + list(additional_rainfall)
        # This method of dict comprehension preserves the order of the dict
        all_rainfall = {date: all_rainfall[date] if date in all_rainfall else additional_rainfall[date] for date in all_dates}
        # stop when we have the desired end date in the dataset
        if desired_end_date in all_rainfall:
            return all_rainfall, is_final
        # data is no longer final after we pass the specified version
        if dataset_revision == latest_rev:
            is_final = False

    # If we don't reach the desired dataset, return all data.
    return all_rainfall, is_final

def get_temperature_dict(lat, lon, dataset_revision, return_metadata=False):
    """
    Build a dict of temperature data for a given grid cell.
    Args:
        lat (float): the latitude of the grid cell, to 3 decimals
        lon (float): the longitude of the grid cell, to 3 decimals
    Returns:
        tuple (highs, lows) of dicts
        highs: dict ({datetime.date: float}) of datetime dates and the corresponding high temperature in degress F
        lows: dict ({datetime.date: float}) of datetime dates and the corresponding low temperature in degress F
    Raises:
        DatasetError: If no matching dataset_revision found on server
        InputOutOfRangeError: If the lat/lon is outside the dataset_revision range in metadata
        CoordinateNotFoundError: If the lat/lon coordinate is not found on server
        DataMalformedError: If the grid cell file can't be parsed as temperature data
    """
    metadata, temp_text = get_dataset_cell(lat, lon, dataset_revision)
    dataset_start_date = datetime.datetime.strptime(metadata['date range'][0], "%Y/%m/%d").date()
    dataset_end_date = datetime.datetime.strptime(metadata['date range'][1], "%Y/%m/%d").date()
    timedelta = dataset_end_date - dataset_start_date
    days_in_record = timedelta.days + 1 # we have both the start and end date in the dataset_revision so its the difference + 1
    day_strs = temp_text.replace(',', ' ').split()
    if (len(day_strs) != days_in_record):
        raise DataMalformedError ("Number of days in data file does not match the provided metadata")
    highs = {}
    lows = {}
    for i in range(days_in_record):
        low, high = map(float, day_strs[i].split('/'))
        date_iter = dataset_start_date + datetime.timedelta(days=i)
        highs[date_iter] = high
        lows[date_iter] = low
    if return_metadata:
        return metadata, highs, lows
    else:
        return highs, lows

def get_rev_temperature_dict(lat, lon, dataset, desired_end_date, latest_rev):
    """
    Build a dictionary of rainfall data. Include as much final data as possible. If the desired end date
    is not in the final dataset, append as much prelim as possible.
    Args:
        lat (float): the latitude of the grid cell, to 3 decimals
        lon (float): the longitude of the grid cell, to 3 decimals
        dataset (str): the dataset name as on hashes.json
        desired_end_date (datetime.date): don't include prelim data after this point if not needed
        latest_rev (str): The least accurate revision that is still considered 'final'
    returns:
        tuple (highs, lows) of dicts and a bool
        highs: dict ({datetime.date: float}) of datetime dates and the corresponding high temperature in degress F
        lows: dict ({datetime.date: float}) of datetime dates and the corresponding low temperature in degress F
        is_final: True if all data is from final dataset, false if prelim included
    """
    highs = {}
    lows = {}
    is_final = True

    # Build the data from the most accurate version of the dataset to the least
    for dataset_revision in dweather_client.ipfs_datasets.datasets[dataset]:
        additional_highs, additional_lows = get_temperature_dict(lat, lon, dataset_revision)
        all_dates = list(highs) + list(additional_highs)    
        highs = {date: highs[date] if date in highs else additional_highs[date] for date in all_dates}
        lows = {date: lows[date] if date in lows else additional_lows[date] for date in all_dates}
        # Stop early if we have the end date
        if desired_end_date in highs:
            return highs, lows, is_final

        # data is no longer final after we pass the specified version
        if dataset_revision == latest_rev:
            is_final = False

    # If we don't reach the desired dataset, return all data.
    return highs, lows, is_final

def get_rev_tagged_temperature_dict(lat, lon, dataset, desired_end_date=None):
    ''' Build temps with a revision tag by each date
    Args:
        lat (float): the grid cell latitude
        lon (float): the grid cell longitude
        dataset (str): the dataset name in ipfs
        desired_end_date (datetime.date): stop early if we get this end date
    returns
        highs: dict with keys of dates, values are tuple (temperature, revision tag) for that date
        lows: dict with keys of dates, values are tuple (temperature, revision tag) for that date
    '''
    highs = {}
    lows = {}

    # Build the data from the most accurate version of the dataset to the least
    for dataset_version in dweather_client.ipfs_datasets.datasets[dataset]:
        additional_highs, additional_lows = get_temperature_dict(lat, lon, dataset_version)
        all_dates = list(highs) + list(additional_highs)    
        highs = {date: highs[date] if date in highs else (additional_highs[date], dataset_version) for date in all_dates}
        lows = {date: lows[date] if date in lows else (additional_lows[date], dataset_version) for date in all_dates}
        # Stop early if we have the end date
        if desired_end_date in highs:
            return highs, lows

    # If we don't reach the desired dataset, return all data.
    return highs, lows

def get_era5_dict(lat, lon, dataset):
    """
    Builds a dict of era5 data
    Args:
        lat (float): the latitude of the grid cell. Will be rounded to one decimal
        lon (float): the longitude of the grid cell. Will be rounded to one decimal
        dataset (str): valid era5 dataset. Currently only 'era5_land_wind_u-hourly', but
        more will be added to ipfs soon
    Returns:
        a dict ({datetime.datetime: float}) of datetimes and the corresponding weather values.
        Units are m/s for the wind datasets
    """
    heads = get_heads()
    era5_hash = heads[dataset]

    snapped_lat, snapped_lon = round(lat, 1), round(lon, 1)
    cpc_lat, cpc_lon = conventional_lat_lon_to_cpc(snapped_lat, snapped_lon)
    formatted_lat, formatted_lon = f"{cpc_lat:08.3f}", f"{cpc_lon:08.3f}"
    url = f"{GATEWAY_URL}/ipfs/{era5_hash}/{formatted_lat}_{formatted_lon}.gz"
    resp = requests.get(url)
    resp.raise_for_status()
    datetime_dict = {}
    with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as gz:
        for i, line in enumerate(gz):
            time_of_year = datetime.datetime(1990 + i, 1, 1)
            data_list = line.decode('utf-8').strip().split(',')
            for point in data_list:
                datetime_dict[time_of_year] = float(point)
                time_of_year += datetime.timedelta(hours=1)
    return (snapped_lat, snapped_lon), datetime_dict





