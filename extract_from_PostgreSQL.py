from aiohttp.client_proto import ResponseHandler
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine
import pandas as pd
import push_to_PostgreSQL

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
            conn.execute("SELECT 1")
        return engine
    except Exception as e:
        print(f"Could not connect to PostgreSQL database: {e}")
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

        # Fallback to downloading fresh data
        df = push_to_PostgreSQL.download_raw_data()
        if isinstance(df, str) and "Error" in df:
            print(f"Error downloading data: {df}")
            return pd.DataFrame()  # Return empty DataFrame instead of None

        df = push_to_PostgreSQL.clean_data(df)
        return df

    finally:
        if engine is not None and hasattr(engine, 'connector'):
            engine.connector.close()