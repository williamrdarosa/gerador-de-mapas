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

""" Dicionário Planilha de Exemplo """
data = {
    'Sigla Estado':['RS','RS'],
    'Município':['Novo Hamburgo','São Leopoldo'],
    'Valores':[80,60]
}

""" Converter Dicionário em DataFrame """
df = pd.DataFrame(data)

""" DataFrame de Download """
dfDownload = pd.DataFrame(data)

""" Extração da Bade de Município """
muni = gpd.read_file('Municipios.geojson')

""" Iniciando o APP com o Tema CERULEAN """
app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN])

""" Layout da Aplicação """
app.layout = html.Div([
    html.Div([
        html.Div([
            dbc.NavbarSimple(
                children=[
                    dbc.Button(
                        "Base para Alimentação",
                        download="data_file.csv",
                        external_link=True,
                        color="success",
                        id="btn-download-txt"
                    ),
                    dcc.Download(id="download-text")
                ],
                brand="Gerador de Mapas",
                brand_href="#",
                color="primary",
                dark=True,
            )
        ]),
    ]), 
    html.Div(children=[
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Arraste e Solte ou ',
                html.A('Selecione o Arquivos')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=True
        ),
        html.Div(id='output-data-upload'),
    ]),
    html.H2(id='explicacao',style={'text-align': 'center'},children=["""Clique no Botão "Base para Alimentação", 
    para baixar o arquivo. Após editar, pode arrastar e soltar o arquivo no navegador."""]),html.H2(id='explicacao2',style={'text-align': 'center'},
    children=["""O Primeiro envio, pode demorar um minuto para ser processardo. Sistema estará baixando os dados do site do IPEA"""]),
])

@app.callback(
    Output("download-text", "data"),
    Input("btn-download-txt", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    """ Função de Download """
    return dcc.send_data_frame(dfDownload.to_excel, "Dados.xlsx", sheet_name="Planilha1", index=False)

def grafico(df):
    """ Função para Gerar o Gráfico """
    df['Município'] = df['Município'].str.title()
    all_muni = muni
    all_muni = all_muni[all_muni['abbrev_state'].isin(list(df['Sigla Estado']))][all_muni['name_muni'].isin(list(df['Município']))]
    all_muni = all_muni.rename(columns={'name_muni': 'Município'})
    all_muni = pd.merge(all_muni, df, how='left', on = 'Município')
    all_muni.index = list(all_muni['Município'])
    fig = px.choropleth_mapbox(all_muni,
        geojson=all_muni.geometry,
        locations=all_muni.index,
        color="Valores",
        opacity=0.5,
        center={"lat": (((mean(list(all_muni.geometry.bounds.maxy))-mean(list(all_muni.geometry.bounds.miny)))/2)+mean(list(all_muni.geometry.bounds.miny)))
        , "lon": (((mean(list(all_muni.geometry.bounds.maxx))-mean(list(all_muni.geometry.bounds.minx)))/2)+mean(list(all_muni.geometry.bounds.minx)))},
        labels={'index':'Município'},
        mapbox_style="open-street-map",
    )
    fig.update_layout(margin=dict(l=1, r=1, t=1, b=1))
    return fig

@app.callback(Output('output-data-upload', 'children'),
            Output('explicacao', 'children'),
            Output('explicacao2', 'children'),
            Input('upload-data', 'contents'),
            State('upload-data', 'filename'),
            State('upload-data', 'last_modified'),
            State('output-data-upload', 'children'),
            State('explicacao', 'children'),
            State('explicacao2', 'children'))
def update_output(list_of_contents, list_of_names, list_of_dates, s1, s2, s3):
    """ Função para imprimir as informações no Layout """
    if list_of_contents is not None:
        children=[
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        children2=[]
        children3=[]
        return [children, children2, children3]
    return [s1, s2, s3]

def parse_contents(contents, filename, date):
    """ Função para Extrair as Informações do Arquivo """
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep=';')
        elif 'xlsx' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'Ocorreu um erro ao processar este arquivo.'
        ])
        
    return html.Div([
        html.Div([
            html.Div([
                html.H1(children=['Mapa'], style={'text-align': 'center'}),
                dbc.Col([
                    dcc.Graph(figure=grafico(df)),
                ],
                style={'width':'100%', 'display': 'inline-block'}
                ),
            ])
        ]),
        html.H5(["Arquivo Enviado: ",filename]),
        html.H6(["Data de Modificação do Arquivo: ",datetime.datetime.fromtimestamp(date)]),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),
        html.Hr(),
    ])

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server()
