import streamlit as st
import pydeck as pdk
import pandas as pd
import json
import time
import os
        
def serve_app(df):    

    # Define a layer to display on a map
    layer = pdk.Layer(
        "IconLayer",
        data=df,
        get_position='[lon, lat]',
        get_icon='icon_data',
        get_size=3,
        pickable=True,
        size_scale=11)

    tooltip = {
    "html": "<b> Station:</b> {name}  <br/> \
            <b> <img src=\"https://img.icons8.com/?size=512&id=257&format=png\" style=\"width:35px;height:35px;\"> {available_bikes} </b> <br/>\
            <b> <img src=\"https://img.icons8.com/?size=512&id=10725&format=png\" style=\"width:35px;height:35px;\"> {available_bike_stands} </b> ",
    "style":{
            "backgroundColor": "white",
            "color": "black",
            "font-family": "verdana",
            "font-size": "300"}
            }
    # Set the viewport location of Brussels
    view_state = pdk.ViewState(latitude=50.8505, longitude=4.3488, zoom=10, bearing=0, pitch=0)
    r = pdk.Deck(map_style=None, initial_view_state=view_state, layers=[layer], tooltip=tooltip)
    plot_spot = st.empty()

    def loc_on_map():
        station = st.session_state["station"]
        if "🔍" not in station: 
            lat = df.loc[df["name"]==station, "lat" ].values[0]
            lon = df.loc[df["name"]==station, "lon" ].values[0]
            view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=15.5, bearing=0, pitch=0)
            r.initial_view_state = view_state
            r.update()
            plot_spot.pydeck_chart(pydeck_obj=r, use_container_width=False)

    if 'station' not in st.session_state:
        plot_spot.pydeck_chart(pydeck_obj=r, use_container_width=False)
    else:
        loc_on_map()

    bar = st.sidebar
    options = ["🔍"]+df["name"].sort_values().to_list()
    bar.selectbox(label="",options=options, key="station")
    col1, col2 = bar.columns([3,3])
    station = st.session_state["station"]
    if "🔍" not in station:
        b = df.loc[df["name"]==station, "available_bikes" ].values[0]
        s = df.loc[df["name"]==station, "available_bike_stands" ].values[0]
        col1.markdown(f"<h1>{b} <img src=\"https://img.icons8.com/?size=512&id=257&format=png\" style=\"width:30px;height:30px;\"> </h1> ", unsafe_allow_html=True)
        col2.markdown(f"<h1>{s} <img src=\"https://img.icons8.com/?size=512&id=10725&format=png\" style=\"width:26px;height:26px;\"> </h1> ", unsafe_allow_html=True)
            

@st.cache_data(ttl=50)
def read_data(link):
    df = pd.read_parquet(link)
    df[["lat", "lon"]] = pd.json_normalize(df["position"].apply(lambda x: json.loads(x)))
    icon_data = {
        "url": "https://img.icons8.com/?size=512&id=52671&format=png",
        "width": 128,
        "height":128,
        "anchorY": 128}
    
    df['icon_data']= None
    for i in df.index:
        df['icon_data'][i] = icon_data
    return df

link = "/opt/bitnami/spark/streampool/bruxelles.parquet"

n_trials = 100
for i in range(n_trials):
    try:
        df = read_data(link)
    except:
        time.sleep(10)
        continue
    break

serve_app(df)



