import pandas as pd
import requests
from datetime import datetime

def download_calfire_data():
    url = 'https://incidents.fire.ca.gov/imapdata/mapdataall.csv'
    try:
        df = pd.read_csv(url)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        raw_filename = f"calfire_raw_{timestamp}.csv"
        df.to_csv(raw_filename, index=False)
        print(f"Raw calfire data saved to {raw_filename}")
        print(f"Data Overview:")
        print(f"Total incidents: {len(df)}")
        print(f"Columns: {df.columns}")
        print(f"Date range: {df['incident_dateonly_created'].min()} to {df['incident_dateonly_created'].max()}")
        print(df.head(3).to_string())
        clean_filename = f"calfire_clean_{timestamp}.csv"
        df.to_csv(clean_filename, index = False)
        return df, clean_filename
    except requests.exceptions.RequestException as e:
        print(e)
        return None, None
    except Exception as e:
        print(e)
        return None, None

if __name__ == "__main__":
    df, filename = download_calfire_data()
    if df is not None:
        print("Success")
    else:
        print("Failed")