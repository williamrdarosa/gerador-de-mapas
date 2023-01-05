import base64
import datetime
import io
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import geobr
import plotly.express as px
from statistics import mean
import pandas as pd
import webbrowser
import pyproj
import geopandas as gpd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE], use_pages=True, update_title='Carregando...', )

app.layout = html.Div(
    # Barra inicial
    [   
        html.Div([
            dash.page_container,
        ],
        style={'margin-top': '1%', 'margin-right': '5%', 'margin-left': '5%', 'margin-bottom': '1%'},
        ),
    ],
)

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server()