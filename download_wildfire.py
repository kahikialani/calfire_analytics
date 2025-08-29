import pandas as pd
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine, text
from datetime import datetime


def database_check(instance_connection_name, db_user, db_pass, db_name='calfire_db'):
    try:
        connector = Connector()
        conn = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=IPTypes.PUBLIC
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT 1 from pg_database WHERE datname = 'calfire_db'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name};")
            print("Database created: ", db_name)
        else:
            print(f"Database {db_name} already exists.")
        return conn
    except Exception as e:
        print(f"Invalid database connection: {e}")
        return None


def create_incidents_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS incidents
                   (
                       id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                       incident_name TEXT NOT NULL,
                       incident_date_created TIMESTAMP,
                       incident_administrative_unit TEXT,
                       incident_county TEXT,
                       incident_location TEXT,
                       incident_acres_burned DOUBLE PRECISION,
                       incident_containment INTEGER,
                       incident_cooperating_agencies TEXT,
                       incident_longitude DOUBLE PRECISION,
                       incident_latitude DOUBLE PRECISION,
                       incident_id TEXT,
                       incident_url TEXT,
                       incident_date_extinguished TIMESTAMP,
                       is_active TEXT,
                       calfire_incident BOOLEAN,
                       data_loaded_date TIMESTAMP DEFAULT NOW
                       );
                   """)
    conn.commit()
    cursor.close()
    print("Table 'incidents' ensured.")


def clean_data(df):
    df = df.drop(columns=['incident_is_final',
                          'incident_date_last_update',
                          'incident_administrative_unit_url',
                          'incident_control',
                          'notification_desired',
                          'incident_dateonly_extinguished',
                          'incident_dateonly_created',
                          'incident_type'], errors='ignore')

    df['incident_date_created'] = pd.to_datetime(df['incident_date_created'], utc=True)
    df['incident_date_extinguished'] = pd.to_datetime(df['incident_date_extinguished'], utc=True)
    return df


def upload_incident_data(df, instance_connection_name, db_user, db_pass):
    engine = get_engine(instance_connection_name, db_user, db_pass)
    if engine is None:
        print("Could not establish database connection for upload")
        return

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df.to_sql("incidents", engine, if_exists="append", index=False, method="multi", chunksize=1000)
        print(f"Data upload complete. Up to date as of {timestamp}")
    except Exception as e:
        print(f"Error uploading data: {e}")
    finally:
        if hasattr(engine, 'connector'):
            engine.connector.close()


def get_engine(instance_connection_name, db_user, db_pass):
    try:
        connector = Connector()

        def getconn():
            return connector.connect(
                instance_connection_name,
                "pg8000",
                user=db_user,
                password=db_pass,
                db="calfire_db",
                ip_type=IPTypes.PUBLIC,
            )

        engine = create_engine("postgresql+pg8000://", creator=getconn)
        engine.connector = connector

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

        print("Database engine created successfully")
        return engine

    except Exception as e:
        print(f"Could not connect to PostgreSQL database: {e}")
        if 'connector' in locals():
            connector.close()
        return None


def load_data(instance_connection_name, db_user, db_pass):
    engine = None
    try:
        engine = get_engine(instance_connection_name, db_user, db_pass)

        if engine is None:
            raise Exception("Database is offline")

        query = "SELECT * FROM incidents ORDER BY incident_date_created DESC;"
        df = pd.read_sql(query, engine)
        return df

    except Exception as e:
        print(f"Could not load data from PostgreSQL: {e}")
        print("Using downloading directly instead.")

        df = download_raw_data()
        if isinstance(df, str) and "Error" in df:
            print(f"Error downloading data: {df}")
            return pd.DataFrame()

        df = clean_data(df)
        return df

    finally:
        if engine is not None and hasattr(engine, 'connector'):
            engine.connector.close()


def download_raw_data():
    url = 'https://incidents.fire.ca.gov/imapdata/mapdataall.csv'
    try:
        data = pd.read_csv(url)
        print(f"Downloaded {len(data)} records from CAL FIRE")
        return data
    except Exception as e:
        print(f"Error downloading raw data: {e}")
        return "Error downloading raw data"


def main(instance_connection_name, db_user, db_pass):
    conn = database_check(instance_connection_name, db_user, db_pass)

    if conn is None:
        print("Unable to connect to database. Using direct download only.")
        data = download_raw_data()
        if isinstance(data, str):
            print("Failed to download data")
            return
        data = clean_data(data)
        print("Data cleaned and ready for use (not uploaded to database)")
    else:
        print("Database connection successful")
        try:
            create_incidents_table(conn)
            data = download_raw_data()

            if isinstance(data, str):
                print("Failed to download data")
                return

            data = clean_data(data)
            upload_incident_data(data, instance_connection_name, db_user, db_pass)
        except Exception as e:
            print(f"Error in main process: {e}")
        finally:
            if conn:
                conn.close()


if __name__ == '__main__':
    instance_connection_name = ''
    db_user = ''
    db_pass = ''
    main(instance_connection_name, db_user, db_pass)