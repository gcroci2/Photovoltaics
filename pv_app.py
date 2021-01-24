import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from dash.dependencies import Input, Output
import numpy as np
import pandas
import json

button1_state = 0
button2_state = 0

customer_feather = 'data/customer_cleansed.feather'
weather_feather = 'data/weather_cleansed.feather'

customer =  pandas.read_feather(customer_feather)
weather = pandas.read_feather(weather_feather)

# mapbox_token = open(".mapbox_token").read()

with open('data/locations.txt') as json_file:
    locations = json.load(json_file)
       
# Build App
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = JupyterDash(__name__, external_stylesheets=external_stylesheets, prevent_initial_callbacks=True)

server = app.server

colors = {
    'background': '#FFFFFF',
    'text': '#091D58',
    'text_sub': '#07AD93',
    'text_site': '#430B95'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children = [
    html.Div(children=[

        html.H1('Pv data visualization', style={'textAlign': 'center', 'color': colors['text']}),

        #---------------------
        html.Div([
            html.Div([

                html.Div([
                    html.Div(children = [
                        html.H3('Substation:', style={'paddingRight': '30px', 'fontSize': 18, 'color': colors['text_sub'], 'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='subs_ticker',
                            options=[
                                {'label': i, 'value': i} for i in customer.Substation.unique()
                                ], multi=True,
                            value=[], 
                            style={'color': colors['text']},
                            placeholder="Select a substation",
                        )
                    ], style={"width": "40%"}, className="six columns"),

                    html.Div([
                        html.H3('Signal:', style={'paddingRight': '30px', 'fontSize': 18, 'color': colors['text_sub'], 'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='signal1_ticker',
                            options=[
                                {'label': i, 'value': i} for i in ['P_GEN', 'Q_GEN', 'S_GEN']
                                ], multi=True,
                            value=[],
                            style={'color': colors['text']}
                        ),
                    ], style={"width": "40%"}, className="six columns"),

                ], className="row"),

                html.Div([
                    html.Div([
                        html.H3('Weather site:', style={'paddingRight': '30px', 'fontSize': 18, 'color': colors['text_site'], 'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='sites_ticker',
                            options=[
                                {'label': i, 'value': i} for i in weather.Site.unique()
                                ], multi=True,
                            value=[],
                            style={'color': colors['text']},
                            placeholder="Select a weather site"
                        ),
                    ], style={"width": "40%"}, className="six columns"),
                    html.Div([
                        html.H3('Signal:', style={'paddingRight': '30px', 'fontSize': 18, 'color': colors['text_site'], 'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='signal2_ticker',
                            options=[
                                {'label': i, 'value': i} for i in ['TempOut', 'SolarRad', 'SolarEnergy', 'HiSolarRad']
                                ], multi=True,
                            value=[],
                            style={'color': colors['text']},
                        ),
                    ], style={"width": "40%"}, className="six columns")
                ], className="row"),

                html.Div([
                    html.H3('Ratios:', style={'paddingRight': '30px', 'fontSize': 18, 'color': colors['text']}),
                    dcc.Dropdown(
                        id='ratio_ticker',
                        options=[
                            {'label': i, 'value': i} for i in [
                                'P_GEN/SolarRad', 'P_GEN/SolarEnergy',
                                'Q_GEN/SolarRad', 'Q_GEN/SolarEnergy',
                                'S_GEN/SolarRad', 'S_GEN/SolarEnergy']
                            ], multi=True,
                        value=[],
                        style={'color': colors['text']},
                    ),
                ], style={"width": "85%"}),

                html.H3('Download displayed traces:', style={'paddingRight': '30px', 'fontSize': 18, 'color': colors['text']}),
                html.Div([
                    html.Div([
                        html.Button("Substations Traces", id="btn1"), Download(id="download1")
                    ], className="six columns", style={"width": "20%", 'color': colors['text']}),
                    html.Div([
                        html.Button("Weather Traces", id="btn2"), Download(id="download2")
                    ], className="six columns", style={"width": "20%", 'color': colors['text'], 'padding-left':'25%'})
                ], className="row"),

            ], className="six columns"),
            #------------------

            html.Div([
                dcc.Graph(id='map')
            ], className="six columns"),
        ], className="row", style={'marginTop': '5em','padding-left':'10%', 'padding-right':'15%', 'verical-align': 'center'}),
        #---------------

        html.Div([
            dcc.Graph(id='graph')
        ], style={'padding-left':'1%', 'padding-right':'1%'}),
        ])

])

###########
@app.callback(Output("download1", "data"),
[Input("btn1", "n_clicks"),
Input('subs_ticker', 'value'),
Input('signal1_ticker', 'value')])
def func(n_clicks, selected_subs, selected_sig1):
    global button1_state
    if n_clicks is not None:
        if n_clicks > button1_state:
            selected_sig1.append('Substation')
            selected_sig1.append('datetime')
            sel_customer = customer[selected_sig1]
            sel_customer = sel_customer[sel_customer['Substation'].isin(selected_subs)]

            button1_state += 1

            return send_data_frame(sel_customer.to_excel, "substations.xls", index=False)


@app.callback(Output("download2", "data"),
[Input("btn2", "n_clicks"),
Input('sites_ticker', 'value'),
Input('signal2_ticker', 'value')])
def func(n_clicks, selected_sites, selected_sig2):
    global button2_state
    if n_clicks is not None:
        if n_clicks > button2_state:
            selected_sig2.append('Site')
            selected_sig2.append('datetime')
            sel_weather = weather[selected_sig2]
            sel_weather = sel_weather[sel_weather['Site'].isin(selected_sites)]

            button2_state += 1

            return send_data_frame(sel_weather.to_excel, "weather.xls", index=False)
################

@app.callback(Output('map', 'figure'),
[Input('subs_ticker', 'value'),
Input('sites_ticker', 'value')])
def update_map(selected_subs, selected_sites):

    fig = go.Figure()

    lat = []
    lon = []
    text = []
    for sub in selected_subs:
        lat.append(locations[sub]['lat'])
        lon.append(locations[sub]['lon'])
        text.append(sub)
    for site in selected_sites:
        lat.append(locations[site]['lat'])
        lon.append(locations[site]['lon'])
        text.append(site)    

    fig = go.Figure(go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14
            ),
            text=text,
        ))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            #accesstoken=mapbox_token,
            bearing=0,
            style = 'open-street-map',
            center=go.layout.mapbox.Center(
                lat=51.89,
                lon=0.93
            ),
            pitch=0,
            zoom=5
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        width=500, 
        height=400
    )

    return fig

@app.callback(Output('graph', 'figure'),
[Input('subs_ticker', 'value'),
Input('signal1_ticker', 'value'),
Input('sites_ticker', 'value'),
Input('signal2_ticker', 'value'),
Input('ratio_ticker', 'value')])
def update_graph(selected_subs, selected_sig1, selected_sites, selected_sig2, selected_ratios):
    fig = go.Figure()

    for x in selected_subs:
        for y in selected_sig1:
            fig.add_trace(go.Scattergl(x=customer[customer.Substation == x].datetime, y=customer[customer.Substation == x][y],
            name = str(x) + ' ' + str(y)))

    for x in selected_sites:
        for y in selected_sig2:
            fig.add_trace(go.Scattergl(x=weather[weather.Site == x].datetime, y=weather[weather.Site == x][y],
            name = str(x) + ' ' + str(y)))

    for sub in selected_subs:
        for site in selected_sites:
            for ratio in selected_ratios: # P_GEN/SolarRad
                weather_upsampled = weather[weather.Site == site].set_index('datetime').resample('10T').asfreq().reset_index()
                denom = weather_upsampled[ratio[6:]]
                num = customer[customer.Substation == sub][ratio[0:5]]
                fig.add_trace(go.Scattergl(x=customer[customer.Substation == sub].datetime, y=num.divide(denom).replace(np.inf, 0),
                name = str(sub) + ' ' + str(ratio[0:5]) + '\\' + str(site) + ' ' + str(ratio[6:])))

    fig.update_traces(
        line={"width": 0.5},
        marker={"size": 3},
        mode="lines+markers",
        showlegend=True
    )

    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        dragmode="zoom", template="plotly_white", legend_orientation="v", xaxis_rangeslider_visible=True,
        xaxis_rangeslider_thickness=0.1, xaxis_rangeslider_bgcolor=colors['text'],
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                    label="1d",
                    step="day",
                    stepmode="backward"),
                    dict(count=1,
                    label="1m",
                    step="month",
                    stepmode="backward"),
                    dict(step="all")
                ])
            )
        ))
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=False) #, port=8051)