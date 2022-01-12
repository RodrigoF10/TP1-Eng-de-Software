import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json

CENTRO_LAT, CENTRO_LONG = -15.798298, -47.876145

#Leitura do Banco de Dados:
con = mysql.connector.connect(host="localhost", database="bd_eng", user="root", password="")
df_estados = pd.read_sql("SELECT * FROM df_estados", con)
df_brasil = pd.read_sql("SELECT * FROM df_brasil", con)

df_estados_ = df_estados[df_estados["data"]=="2021-03-13"]
df_data = df_estados[df_estados["estado"]=="MG"]

#df_estados.columns =
selecao_colunas = {"casosAcumulado": "Casos Acumulados",
                   "casosNovos": "Novos Casos",
                   "obitosAcumulado": "Óbitos Acumulados",
                   "obitosNovos": "Óbitos por dia"}

#Leitura do geo.json
estados_brasil = json.load(open("brazil_geo.json", "r"))

#Instâncias

TEMA = "bootstrap.min.css"
app = dash.Dash(__name__,external_stylesheets=[TEMA])

mapa = px.choropleth_mapbox(
    df_estados_, locations="estado", color="casosNovos", center={"lat":-15.798298, "lon":-47.876145},
    zoom=4, geojson=estados_brasil, color_continuous_scale="Sunsetdark", opacity=0.4, hover_data=
    {"casosAcumulado": True, "casosNovos": True, "obitosNovos": True, "estado": True}
)

mapa.update_layout(
    paper_bgcolor="#242424",
    autosize=True,
    margin=go.layout.Margin(l=0, r=0, t=0, b=0),
    showlegend=False,
    mapbox_style="carto-darkmatter"
)

graf_linha = go.Figure()
graf_linha.add_trace(
    go.Scatter(x=df_data["data"], y=df_data["casosAcumulado"])
)

graf_linha.update_layout(
    paper_bgcolor="#242424",
    plot_bgcolor="#242424",
    autosize=True,
    margin=dict(l=10, r=10, t=10, b=10)
)
#Layout

app.layout = dbc.Container(
    dbc.Row([
        dbc.Col([
            html.Div([
            html.Img(id="logo", src=app.get_asset_url("covid.png"), height=50),
            html.H5("Evolução do COVID-19"),
            dbc.Button("BRASIL", color="primary", id="location-button", size="lg")], style={}),
            html.P("Informe a data desejada:", style={"margin-top":"40px"}),
            html.Div(id="div-test", children= [dcc.DatePickerSingle(id="date-picker",
                        min_date_allowed=df_brasil["data"].min(),
                        max_date_allowed=df_brasil["data"].max(),
                        initial_visible_month=df_brasil["data"].min(),
                        date=df_brasil["data"].max(),
                        display_format="DD/MM/YYYY",
                        style={"border": "0px solid black"})]
                        ),
                dbc.Row([
                        dbc.Col([dbc.Card([
                                dbc.CardBody([
                                    html.Span("Casos recuperados", className="card-text"),
                                    html.H3(style={"color": "#adfc92"}, id="casos-recuperados-text"),
                                    html.Span("Em acompanhamento", className="card-text"),
                                    html.H5(id="em-acompanhamento-text"),
                                    ])
                                ], color="light", outline=True, style={"margin-top": "10px",
                                        "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                        "color": "#FFFFFF"})], md=4),
                        dbc.Col([dbc.Card([
                                dbc.CardBody([
                                    html.Span("Casos confirmados totais", className="card-text"),
                                    html.H3(style={"color": "#389fd6"}, id="casos-confirmados-text"),
                                    html.Span("Novos casos na data", className="card-text"),
                                    html.H5(id="novos-casos-text"),
                                    ])
                                ], color="light", outline=True, style={"margin-top": "10px",
                                        "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                        "color": "#FFFFFF"})], md=4),
                        dbc.Col([dbc.Card([
                                dbc.CardBody([
                                    html.Span("Óbitos confirmados", className="card-text"),
                                    html.H3(style={"color": "#DF2935"}, id="obitos-text"),
                                    html.Span("Óbitos na data", className="card-text"),
                                    html.H5(id="obitos-na-data-text"),
                                    ])
                                ], color="light", outline=True, style={"margin-top": "10px",
                                        "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                        "color": "#FFFFFF"})], md=4),
                    ]),
        html.Div([
            html.P("Selecione o tipo de dado desejado:", style={"margin-top":"25px"}),
            dcc.Dropdown(
                id="location-dropdown",
                options=[{"label": j,"value": i} for i, j in selecao_colunas.items()],
                value="casosNovos",
                style={"margin-top":"10px"}
            ),
            dcc.Graph(id="line-graph", figure=graf_linha)
            ])
    ], md=5, style={"padding": "25px", "background-color": "#242424"}),
        dbc.Col([
            dcc.Loading(id="loading-1", type="default", children=
                dcc.Graph(id="choropleth-map", figure=mapa, style={"height":"100vh", "margin-right":"10px"}))
            ], md=7)
    ], className="g-0"),
    fluid=True)

#Interatividade:
date = "20/09/2021"
location="Minas Gerais"
@app.callback(
    [Output("casos-recuperados-text", "children"),
     Output("em-acompanhamento-text", "children"),
     Output("casos-confirmados-text", "children"),
     Output("novos-casos-text", "children"),
     Output("obitos-text", "children"),
     Output("obitos-na-data-text", "children")
     ],
    [Input("date-picker", "date"), Input("location-button", "children")]
)
def display_status(date, location):
    if location=="BRASIL":
        df_data_on_date=df_brasil[df_brasil["data"]==date]
    else:
        df_data_on_date=df_estados[(df_estados["estado"]==location) & (df_estados["data"]==date)]

    recuperados_novos = "-" if df_data_on_date["Recuperadosnovos"].isna().values[0] else f'{int(df_data_on_date["Recuperadosnovos"].values[0]):,}'.replace(",", ".")
    acompanhamento = "-" if df_data_on_date["emAcompanhamentoNovos"].isna().values[0] else f'{int(df_data_on_date["emAcompanhamentoNovos"].values[0]):,}'.replace(",", ".")
    acumulados = "-" if df_data_on_date["casosAcumulado"].isna().values[0] else f'{int(df_data_on_date["casosAcumulado"].values[0]):,}'.replace(",", ".")
    casos_novos = "-" if df_data_on_date["casosNovos"].isna().values[0] else f'{int(df_data_on_date["casosNovos"].values[0]):,}'.replace(",", ".")
    obitos_acumulados = "-" if df_data_on_date["obitosAcumulado"].isna().values[0] else f'{int(df_data_on_date["obitosAcumulado"].values[0]):,}'.replace(",", ".")
    obitos_novos = "-" if df_data_on_date["obitosNovos"].isna().values[0] else f'{int(df_data_on_date["obitosNovos"].values[0]):,}'.replace(",", ".")


    return (recuperados_novos, acompanhamento, acumulados, casos_novos, obitos_acumulados, obitos_novos,)

@app.callback(Output("line-graph", "figure"),[
    Input("location-dropdown", "value"), Input("location-button", "children")
])
def plot_line_graph(plot_type, location):
    if location=="BRASIL":
        df_data_on_location = df_brasil.copy()
    else:
        df_data_on_location = df_estados[(df_estados["estado"] == location)]

    bar_plots = ["casosNovos", "obitosNovos"]
    graf_barra = go.Figure(layout={"template":"plotly_dark"})
    if plot_type in bar_plots:
        graf_barra.add_trace(go.Bar(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))
    else:
        graf_barra.add_trace(go.Scatter(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))

    graf_barra.update_layout(
    paper_bgcolor="#242424",
    plot_bgcolor="#242424",
    autosize=True,
    margin=dict(l=10, r=10, t=10, b=10)
    )

    return graf_barra

@app.callback(
    Output("choropleth-map", "figure"),
    [Input("date-picker", "date")]
)
def update_mapa(date):
    df_data_on_states = df_estados[df_estados["data"] == date]

    mapa = px.choropleth_mapbox(df_data_on_states, locations="estado", geojson=estados_brasil,
        center={"lat": CENTRO_LAT, "lon": CENTRO_LONG},
        zoom=4, color="casosAcumulado", color_continuous_scale="Redor", opacity=0.55,
        hover_data={"casosAcumulado": True, "casosNovos": True, "obitosNovos": True, "estado": False}
        )

    mapa.update_layout(paper_bgcolor="#242424", mapbox_style="carto-darkmatter", autosize=True,
                    margin=go.layout.Margin(l=0, r=0, t=0, b=0), showlegend=False)
    return mapa

@app.callback(
    Output("location-button", "children"),
    [Input("choropleth-map", "clickData"), Input("location-button", "n_clicks")]
)
def update_location(click_data, n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if click_data is not None and changed_id != "location-button.n_clicks":
        state = click_data["points"][0]["location"]
        return "{}".format(state)

    else:
        return "BRASIL"

if __name__ == "__main__":
    app.run_server(debug=True)
