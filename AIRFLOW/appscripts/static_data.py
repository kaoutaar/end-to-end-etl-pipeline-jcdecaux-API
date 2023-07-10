import json
import requests
from sqlalchemy import create_engine
import pandas as pd

pd.set_option('display.max_columns', 30)



def send_static_data():
    con_col = ['Cont_name', 'Commercial_name', 'Country_code']
    sta_col = ['Cont_name', 'Station_name', 'Station_address', 'Banking','Bonus', 'Latitude', 'Longitude']

    key = "c1d0cfc0377b8d04d9179d1c3f7a80e2491b30c3"
    contracts_url = f"https://api.jcdecaux.com/vls/v1/contracts?&apiKey={key}"
    stations_url = f"https://api.jcdecaux.com/vls/v1/stations?&apiKey={key}"
    server = 'mssql'

    resp_contracts = requests.get(contracts_url)
    resp_stations = requests.get(stations_url)

    contracts = pd.read_json(resp_contracts.text).drop('cities', axis=1)
    contracts.columns = con_col
    stations = pd.json_normalize(json.loads(resp_stations.text))[["contract_name","name", "address","banking","bonus",  "position.lat", "position.lng"]]
    stations.columns = sta_col


    driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    driver = "ODBC+Driver+17+for+SQL+Server"
    url = f"mssql+pyodbc://sa:MY1password@{server}:1433/velib?driver={driver}"
    engine = create_engine(url)
    contracts.to_sql("Contracts", con=engine, if_exists='append', index=False)
    stations.to_sql("Stations", con=engine, if_exists='append', index=False)