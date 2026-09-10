from ingestion.extract_weather import extract_weather
from ingestion.load_postgres import load_raw_weather

DATABASE_URL = (
    "postgresql+psycopg2://warehouse_user:"
    "warehouse_password@localhost:5432/warehouse"
)

df = extract_weather(
    lat=27.7,
    lon=85.3,
)

load_raw_weather(
    df=df,
    database_url=DATABASE_URL,
    lat=27.7,
    lon=85.3,
)
