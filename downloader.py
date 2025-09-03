import requests
import logging
import pandas as pd
from io import StringIO

class WildfireDownloader:
    def __init__(self):
        self.url = 'https://incidents.fire.ca.gov/imapdata/mapdataall.csv'

    def calfire_download(self):
        try:
            raw_data = pd.read_csv(self.url)
            logging.debug(f"Downloaded {len(raw_data)} records from CAL FIRE")
            df = self.clean_data(raw_data)
            return df
        except Exception as e:
            logging.error(f"Could not download data from CAL FIRE: {e}")

    def clean_data(self, raw_data):
        logging.debug(f"Cleaning data from {len(raw_data)} records")
        df = raw_data.drop(columns=['incident_is_final',
                              'incident_date_last_update',
                              'incident_administrative_unit_url',
                              'incident_control',
                              'notification_desired',
                              'incident_dateonly_extinguished',
                              'incident_dateonly_created',
                              'incident_type'], errors='ignore')
        df['incident_date_created'] = pd.to_datetime(df['incident_date_created'], utc=True)
        df['incident_date_extinguished'] = pd.to_datetime(df['incident_date_extinguished'], utc=True)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df



class PrecipDownloader:
    def __init__(self):
        self.base_url = 'https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/time-series/'
        self.end_url = '/pcp/ytd/0/2014-2025/data.csv'
        self.ca_county_codes = [
            "CA-001", "CA-003", "CA-005", "CA-007", "CA-009", "CA-011", "CA-013", "CA-015", "CA-017", "CA-019",
            "CA-021", "CA-023", "CA-025", "CA-027", "CA-029", "CA-031", "CA-033", "CA-035", "CA-037", "CA-039",
            "CA-041", "CA-043", "CA-045", "CA-047", "CA-049", "CA-051", "CA-053", "CA-055", "CA-057", "CA-059",
            "CA-061", "CA-063", "CA-065", "CA-067", "CA-069", "CA-071", "CA-073", "CA-075", "CA-077", "CA-079",
            "CA-081", "CA-083", "CA-085", "CA-087", "CA-089", "CA-091", "CA-093", "CA-095", "CA-097", "CA-099",
            "CA-101", "CA-103", "CA-105", "CA-107", "CA-109", "CA-111", "CA-113", "CA-115"
        ]
        self.ca_county_names = county_names = [
    "Alameda County, CA","Alpine County, CA","Amador County, CA","Butte County, CA","Calaveras County, CA",
    "Colusa County, CA","Contra Costa County, CA","Del Norte County, CA","El Dorado County, CA","Fresno County, CA",
    "Glenn County, CA","Humboldt County, CA","Imperial County, CA","Inyo County, CA","Kern County, CA",
    "Kings County, CA","Lake County, CA","Lassen County, CA","Los Angeles County, CA","Madera County, CA",
    "Marin County, CA","Mariposa County, CA","Mendocino County, CA","Merced County, CA","Modoc County, CA",
    "Mono County, CA","Monterey County, CA","Napa County, CA","Nevada County, CA","Orange County, CA",
    "Placer County, CA","Plumas County, CA","Riverside County, CA","Sacramento County, CA","San Benito County, CA",
    "San Bernardino County, CA","San Diego County, CA","San Francisco County, CA","San Joaquin County, CA","San Luis Obispo County, CA",
    "San Mateo County, CA","Santa Barbara County, CA","Santa Clara County, CA","Santa Cruz County, CA","Shasta County, CA",
    "Sierra County, CA","Siskiyou County, CA","Solano County, CA","Sonoma County, CA","Stanislaus County, CA",
    "Sutter County, CA","Tehama County, CA","Trinity County, CA","Tulare County, CA","Tuolumne County, CA",
    "Ventura County, CA","Yolo County, CA","Yuba County, CA"
]
        self.clean_names = [name.replace(" County, CA", "").replace(", CA", "") for name in county_names]
        self.county_dictionary = dict(zip(self.ca_county_codes, self.clean_names))
        logging.debug(f"County Dictionary: {self.county_dictionary}")

    def get_county_df(self, county_code):
        url = f"{self.base_url}{county_code}{self.end_url}"
        response = requests.get(url)
        if response.status_code == 200:
            csv_data = response.text
            df = pd.read_csv(StringIO(csv_data))
            df = df.drop(range(2))
            df.columns = ['precip_date','precip_inches']
            df['precip_inches'] = df['precip_inches'].astype(float)
            df['precip_date'] = pd.to_datetime(df['precip_date'], format = '%Y%m')
            df['precip_month'] = pd.to_datetime(df['precip_date']).dt.month
            df['precip_year'] = pd.to_datetime(df['precip_date']).dt.year
            df['county'] = self.county_dictionary[county_code]
            logging.info(f"DF Loaded: {county_code}")
            return df
        else:
            logging.error(f"Error downloading data: {response.status_code}")
            return None

    def precip_download(self):
        precip_df = pd.DataFrame()
        for code in self.ca_county_codes:
            precip_df = pd.concat([precip_df, self.get_county_df(county_code = code)], ignore_index=True)
        precip_df.to_csv('county_precipitation_data.csv', index=False)
        logging.info(f"Created csv with {len(precip_df)} rows")
        precip_df = precip_df.loc[:, ~precip_df.columns.str.contains('^Unnamed')]
        return precip_df

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')