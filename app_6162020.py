# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 10:09:03 2020
@author: Andrew Hong
"""
import pandas as pd
from pandas import melt
import datetime as dt
import numpy as np

import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go

from urllib.request import urlopen
import json

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

'''datasets'''

#####removed about 150 lines of code that was data prep######

'''functions'''
unemployment_rate_range = (county_unemp_df[county_unemp_df["Data Type"]=="Unemployment Rate"]["Value"].min(),
                            county_unemp_df[county_unemp_df["Data Type"]=="Unemployment Rate"]["Value"].max())

unemployment_range = (county_unemp_df[county_unemp_df["Data Type"]=="Unemployment"]["Value"].min(),
                            county_unemp_df[county_unemp_df["Data Type"]=="Unemployment"]["Value"].max()*0.2)

employment_range = (county_unemp_df[county_unemp_df["Data Type"]=="Employment"]["Value"].min(),
                            county_unemp_df[county_unemp_df["Data Type"]=="Employment"]["Value"].max()*0.2)

laborforce_range = (county_unemp_df[county_unemp_df["Data Type"]=="Labor Force"]["Value"].min(),
                            county_unemp_df[county_unemp_df["Data Type"]=="Labor Force"]["Value"].max()*0.2)

select_county_data_range = {"Unemployment Rate": unemployment_rate_range,
                            "Unemployment": unemployment_range,
                            "Employment": employment_range,
                            "Labor Force": laborforce_range}

income_range = (0,100000) 
error_range = (-10000,10000)
population_range = (0,1000000)

select_census_range = {"income2018": income_range, "error2018": error_range, "population":population_range}

def plot_unemploy_choro_county(df,rangesize,datatype):
    fig_map = px.choropleth_mapbox(df, geojson=counties, locations='fips', color='Value',
                                color_continuous_scale="Reds",
                                range_color=rangesize,
                                mapbox_style="carto-positron",
                                zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                                opacity=0.5,
                                hover_data=["County","Value"],
                              )
    fig_map.update_layout(
        title_text = '{} by County'.format(datatype),
        margin={"r":10,"t":0,"l":0,"b":0},
        )
    return fig_map

def plot_unemploy_choro_state(df, industry):
    fig = go.Figure(data=go.Choropleth(
        locations=df['State'], # Spatial coordinates
        z = df['Employment'], # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        zmin=-60,
        zmax=20,
        reversescale=True,
        colorbar_title = 'MoM % Change',
    ))
    
    fig.update_layout(
        title_text = 'Monthly Change in Employment in {} by State'.format(industry),
        geo_scope='usa', # limite map scope to USA
    )
    return fig

"""dash app"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

#for dropdown menus
available_counties = county_unemp_df['County'].unique()
available_data_type = county_unemp_df["Data Type"].unique()
available_states = county_unemp_df['State'].unique()
available_stateandcounty = county_unemp_df['County and State'].unique()

available_industries = state_unemp_df["Industry"].unique()
available_datasets = ["Census Data","Unemployment Data"]

'''exploring_data_tab'''
map_charts = dbc.Card(
                   dbc.CardBody([
                       dbc.Col([
                            html.H3('Select One Industry to Observe'), #change this to value to observe, since click or search will be for county
                                dcc.Dropdown(
                                    id='Industry Search',
                                    options=[{'label': i, 'value': i} for i in available_industries]
                                    , value="Leisure  Hospitality",
                                    multi=False
                                    ),
                                
                            html.Label('Select Month:'),
                                dcc.Slider(
                                    id='state-month-selector',
                                    min=state_unemp_df['Month'].min(),
                                    max=state_unemp_df['Month'].max(),
                                    value=4,
                                    marks={str(year): str(year) for year in state_unemp_df['Month'].unique()},
                                    step=None
                                ),
                            
                           html.Label('Select Year:'),
                               dcc.Slider(
                                    id='state-year-selector',
                                    min=state_unemp_df['Year'].min(),
                                    max=state_unemp_df['Year'].max(),
                                    value=state_unemp_df['Year'].max(),
                                    marks={str(year): str(year) for year in state_unemp_df['Year'].unique()},
                                    step=None
                                ),
                
                            dcc.Graph(id='statemap',style={'height': '600px'}),
                                                                   
                            html.H3('Select Data Set to Observe'), #change this to value to observe, since click or search will be for county
                                    dcc.Dropdown(
                                        id='Data Set Type',
                                        options=[{'label': i, 'value': i} for i in available_datasets]
                                        , value="Unemployment Data",
                                        multi=False
                                        ),
                                    
                            html.H3('Select Data Type to Observe'), #change this to value to observe, since click or search will be for county
                                    dcc.Dropdown(
                                        id='Data Type',
                                        options=[{'label': i, 'value': i} for i in available_data_type] #fix this too 
                                        , value="Unemployment Rate",
                                        multi=False
                                        ),
                                    
                            html.Label(''), #create space
                            dcc.Graph(id='countymap',style={'height': '600px'}), #county unemp
                            
                            ], ), #left column
                       ]),
                   )
               
normal_charts = dbc.Card(
    dbc.CardBody([
        dbc.Col([
             html.H3('Select a State (Recommended since County names are not unique)'), #change this to value to observe, since click or search will be for county
                 dcc.Dropdown(
                     id='state search',
                     options=[{'label': i, 'value': i} for i in available_states]
                     , value="NY",
                     multi=False
                     ),     
                 
             html.Label(''), #create space

             html.H3('Select a County'), #change this to value to observe, since click or search will be for county
                 dcc.Dropdown(
                     id='county search',
                     options=[{'label': i, 'value': i} for i in available_counties]
                     , value="New York County",
                     multi=False
                     ),                
            
            dbc.Alert(
                [
                    "Charts will be empty if no county is selected",
                ],
                id="alert-empty",
                dismissable=True,
                fade=True,
                is_open=True,
                color="danger",
                ),
            
             dbc.Row([
                 dbc.Col(
                     dcc.Graph(id='county trends',style={'height': '500px'}), #line chart
                     width=6),
                 
                 dbc.Col(
                     dcc.Graph(id='racial',style={'height': '500px'}), #bar chart
                     width=6),
                 ],),
             

                 dbc.Col(
                     dcc.Graph(id='state employment',style={'height': '500px'}), #bar chart
                     ),
                 
                 dbc.Col(
                     dcc.Graph(id='met employment',style={'height': '500px'}), #bar chart
                     ),
           
             ], ), #right column
      ]),
    ),

exploring_data_tab = dbc.Card(
        dbc.CardBody([
              dbc.Row([dbc.Col(map_charts,width=6), dbc.Col(normal_charts,width=6)]),        
            ]),
        className="mt-3",
        ) #card end

'''comparing_data_tab'''

state_comparisons = dbc.Card(
    dbc.CardBody([

                     html.H3('Select Multiple States'), #change this to value to observe, since click or search will be for county
                         dcc.Dropdown(
                             id='state multiselect',
                             options=[{'label': i, 'value': i} for i in available_states]
                             , value=["NY","LA"],
                             multi=True
                             ),   
                         
                    dcc.Graph(id='state industries comparison',style={'height': '500px'}), #bar chart

                ],),
    )

county_comparisons = dbc.Card(
                        dbc.CardBody([

                                     html.H3('Select Multiple Counties'), #change this to value to observe, since click or search will be for county
                                        dcc.Dropdown(
                                            id='county multiselect',
                                            options=[{'label': i, 'value': i} for i in county_unemp_df['County and State'].unique()]
                                            , value=["New York County, NY","Los Angeles County, CA"],
                                            multi=True
                                            ),     
                                     
                                     dcc.Graph(id='county trends comparison',style={'height': '500px'}), #line chart

                                     dcc.Graph(id='county race comparison',style={'height': '500px'}),       
                                     
                                     dcc.Graph(id='income comparison',style={'height': '500px'}),   
 
                            ],),
                    )

comparing_data_tab = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(state_comparisons,width=6), dbc.Col(county_comparisons,width=6)]),
        ]
    ),
className="mt-3",
)

'''author tab'''
author_tab = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row([
                html.H2('Created by Andrew Hong'),
            ]),
            
            dbc.Row([
                html.Label('This dashboard was created to help track unemployment through the Covid19 crisis, and see where disparities pop up during recovery. Please check the Medium blog post for data sourcing and methodology.'),
            ]),
            
            dbc.Row([
                dcc.Link('Medium Page', href="https://medium.com/@andrew.hong"),
            ]),
            
            dbc.Row([
                dcc.Link('LinkedIn', href = "https://www.linkedin.com/in/andrew-hong-nyu/"),
            ]),
            
            dbc.Row([
                dcc.Link('Buy Me a Coffee and keep this dashboard running!', href = "https://www.buymeacoffee.com/tsuyeehong"),
            ]),
        ]
    ),
className="mt-3",
)

'''app layout'''
app.layout = html.Div([

    dbc.Tabs([
        dbc.Tab(exploring_data_tab, label="Exploring Data"),
        dbc.Tab(comparing_data_tab, label="Comparing Data"),
        dbc.Tab(author_tab, label="About Me", tab_style={"margin-left": "auto"}, label_style={"color": "#00AEF9"}),
        ])
    ])

"""exploring_data_tab callbacks"""
#'''setting options'''
@app.callback(
    Output('county search', 'options'),
    [Input('state search', 'value')])
def set_counties_options(selected_state):
    if(len(selected_state)!=0):
        avail_count = state_county_dropdown[selected_state].dropna()
        return [{'label': i, 'value': i} for i in avail_count]
    avail_count = county_unemp_df['County'].unique()
    return [{'label': i, 'value': i} for i in avail_count]

@app.callback(
    Output('Data Type', 'options'),
    [Input('Data Set Type', 'value')])
def set_data_type(selected_data):
    if selected_data=="Census Data":
        available_data_type = demo_df_income["Income"].unique()
        return [{'label': i, 'value': i} for i in available_data_type]
    available_data_type = county_unemp_df["Data Type"].unique()
    return [{'label': i, 'value': i} for i in available_data_type]

@app.callback(
    Output("alert-empty", "is_open"),
    [Input("county search", "value")],
    [State("alert-empty", "is_open")],
)
def toggle_alert_no_fade(value, is_open):
    if not value:
        print(is_open)
        return True
    else:
        return False

#'''charts'''
@app.callback(
    Output('statemap','figure'),
    [Input('Industry Search','value'),
     Input('state-month-selector','value'),
     Input('state-year-selector','value')])
def update_state_figure(industry, selected_month,selected_year):
    #select county
    temp_df = state_unemp_df[state_unemp_df["Industry"]==industry]
    
    #filter date
    temp_df = temp_df[temp_df["Year"] == selected_year]
    temp_df = temp_df[temp_df["Month"] == selected_month]
    
    return plot_unemploy_choro_state(temp_df, industry)

#add change fig 
@app.callback(
    Output('countymap','figure'),
    [ Input('Data Type','value'),
      Input('state-month-selector','value'),
      Input('state-year-selector','value'),
      Input('Data Set Type','value')])
def update_county_figure(datatype,selected_month,selected_year,datasettype):
    #filter date
    if datasettype=="Unemployment Data":
        temp_df = county_unemp_df[county_unemp_df["Data Type"] == datatype]
        temp_df = temp_df[temp_df["Year"] == selected_year]
        temp_df = temp_df[temp_df["Month"] == selected_month]
        fig = plot_unemploy_choro_county(temp_df,select_county_data_range[datatype],datatype)
   
    if datasettype=="Census Data":
        temp_df = demo_df_income[demo_df_income["Income"]==datatype]
        fig = plot_unemploy_choro_county(temp_df,select_census_range[datatype],datatype)
   
    return fig

@app.callback(
    Output('racial', 'figure'),
    [Input('county search', 'value')])
def update_race_distribution(county):   
    pivot = demo_df[demo_df["County"]==county]
    pivot = pivot.pivot_table(index="County",columns="Race",values="% of Population",aggfunc=np.mean)
    pivot = pivot.T
    fig = px.bar(pivot, x=county, y=pivot.index, title="Percent Popluation by Race")
    fig.update_xaxes(range=[0, 100])
    return fig

#add hoverdata for date?
@app.callback(
    Output('met employment', 'figure'),
    [Input('county search', 'value')])
def update_met_reliance(county):
    met_area = FipstoCbsaConverter[CountyFipsConverter[county]]
    pivot = met_area_unemp_df.pivot_table(index="Met Area", columns = "Industry", values = "Employment", aggfunc=np.mean)
    pivot = pivot.fillna(0)
    pivot = pivot.loc[:, met_industry_columns].div(pivot.loc[:, 'Total Nonfarm'], axis=0)*100    
    
    pivot = pivot.T
    pivot = pivot[met_area]
    pivot = pivot[pivot!=0]
    fig = px.bar(pivot, x=met_area, y=pivot.index, title="Closest Metropolitan Area Percent Employment By Industry (if any)")
    fig.update_xaxes(range=[0, 60])
    return fig

#add hoverdata for date?
@app.callback(
    Output('state employment', 'figure'),
    [Input('county search', 'value')])
def update_state_reliance(county):
    state = CountyStateConverter[county]
    pivot = state_unemp_df_notional.pivot_table(index="State", columns = "Industry", values = "Employment", aggfunc=np.mean)
    pivot = pivot.fillna(0)
    pivot = pivot.loc[:,state_industry_columns].div(pivot.loc[:, 'Total Nonfarm'], axis=0)*100    
    
    pivot = pivot.T
    pivot = pivot[state]
    pivot = pivot[pivot!=0]
    fig = px.bar(pivot, x=state, y=pivot.index, title="{} Percent Employment By Industry".format(state))
    fig.update_xaxes(range=[0, 60])
    return fig

@app.callback(
    Output('county trends', 'figure'),
    [Input('county search', 'value')])
def update_county_trends(county):
    temp_df = county_unemp_df[county_unemp_df["County"]==county]
    pivot = temp_df[temp_df["Data Type"]=="Unemployment Rate"].pivot_table(index="Date", values="Value",aggfunc="sum")
    return px.line(pivot, x=pivot.index,y="Value", title="{} Unemployment Rate History".format(county))

"""comparing_data_tab callbacks"""

@app.callback(
    Output('county trends comparison', 'figure'),
    [Input('county multiselect', 'value')])
def compare_county_trends(selected_counties):
    temp_df = county_unemp_df[county_unemp_df["County and State"].isin(selected_counties)]
    temp_df = temp_df[temp_df["Data Type"]=="Unemployment Rate"]
    return px.line(temp_df, x="Date",y="Value", color="County", title="Unemployment Rate History")

@app.callback(
    Output('state industries comparison', 'figure'),
    [Input('state multiselect', 'value')])
def compare_industry_county_trends(selected_states):
    pivot = state_unemp_df_notional[state_unemp_df_notional["State"].isin(selected_states)]
    
    pivot = pivot.pivot_table(index="State", columns = "Industry", values = "Employment", aggfunc=np.mean)
    pivot = pivot.fillna(0)
    pivot = pivot.loc[:,pivot.columns != 'Total Nonfarm'].div(pivot.loc[:, 'Total Nonfarm'], axis=0)*100    
    
    pivot = pivot.T
    pivot = pivot.unstack()
    pivot = pivot.reset_index()
    pivot.columns = ["State","Industry","% Employed in Industry"]
    return px.bar(pivot, x="State", y="% Employed in Industry", color = "Industry", title="Percent Employment By Industry")

@app.callback(
    Output('county race comparison', 'figure'),
    [Input('county multiselect', 'value')])
def compare_county_race_trends(selected_counties):
    pivot = demo_df[demo_df["County and State"].isin(selected_counties)]
    return px.bar(pivot, x="County and State", y="% of Population", color = "Race", title="Percent Race of County Population")

@app.callback(
    Output('income comparison', 'figure'),
    [Input('county multiselect', 'value')])
def compare_county_race_trends(selected_counties):
    pivot = demo_df_income[demo_df_income["County and State"].isin(selected_counties)]
    pivot = pivot[pivot["Income"]=="income2018"]
    return px.bar(pivot, x="County and State", y="Value", title="Mean Income of County")


if __name__ == '__main__':
    app.run_server(debug=False)