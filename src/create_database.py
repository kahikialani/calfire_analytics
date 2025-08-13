import sqlite3
import pandas as pd
import os
from datetime import datetime

def create_database():
    db_name = 'calfire_data.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_name TEXT NOT NULL,
            incident_is_final TEXT,
            incident_date_last_update TEXT,
            incident_date_created TEXT,
            incident_administrative_unit TEXT,
            incident_administrative_unit_url TEXT,
            incident_county TEXT,
            incident_location TEXT,
            incident_acres_burned REAL,
            incident_containment INTEGER,
            incident_control INTEGER,
            incident_cooperating_agencies TEXT,
            incident_longitude REAL,
            incident_latitude REAL,
            incident_type TEXT,
            incident_id TEXT,
            incident_url TEXT,
            incident_date_extinguished TEXT,
            incident_dateonly_extinguished TEXT,
            incident_dateonly_created TEXT,
            is_active TEXT,
            calfire_incident TEXT,
            notification_desired TEXT,
            data_loaded_date TEXT
        )
    """)
    conn.commit()
    print(f"Database {db_name} created")
    return conn

def load_csv_to_database(csv_filename, conn):
    print("Loading csv to database")
    try:
        df = pd.read_csv(csv_filename)
        print(f"Found {len(df)} rows")
        df['data_loaded_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df.to_sql('incidents', conn, if_exists = "replace", index=False)
        print(f"Successfully created {len(df)} rows in database")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM incidents")
        total_records = cursor.fetchone()[0]
        print(f"Total records: {total_records}")
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def query_database(conn):
    print("Querying database")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM incidents")
        total = cursor.fetchone()[0]
        cursor.execute("""
        SELECT incident_name, incident_acres_burned, incident_county
        FROM incidents
        WHERE incident_acres_burned > 100000
        ORDER BY incident_acres_burned DESC
        LIMIT 5
        """)
        large_fires = cursor.fetchall()
        print(f"Top 5 fires: {large_fires}")
        for fire in large_fires:
            name, acres, county = fire
            print(f"\t{name}\t{acres}\t{county}")
        cursor.execute("""
        SELECT incident_county, COUNT(*) as incident_count
        FROM incidents
        WHERE incident_county IS NOT NULL AND incident_county != ''
        GROUP BY incident_county
        ORDER BY incident_county DESC
        LIMIT 5
        """)
        counties = cursor.fetchall()
        print(f"Top 5 counties: {counties}")
        for county, count in counties:
            print(f"{county}:{count} total incidents")
    except Exception as e:
        print(f"Error in query: {e}")
        return False

def find_latest_csv():
    csv_files = [f for f in os.listdir('.') if f.startswith('calfire_') and f.endswith('.csv')]
    if not csv_files:
        print("No csv files found, run download script")
    latest_file = sorted(csv_files)[-1]
    print(f"Latest csv file: {latest_file}")
    return latest_file

if __name__ == "__main__":
    print("Creating database")
    csv_file = find_latest_csv()
    if csv_file:
        conn = create_database()
        success = load_csv_to_database(csv_file, conn)
        if success:
            query_database(conn)
            print("Successfully created database")
    else:
        print("Failed to create database")