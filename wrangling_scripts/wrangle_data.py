import pandas as pd
import plotly.graph_objs as go

import numpy as np
# from matplotlib import dates
from collections import defaultdict

# This file is used to read in data and prepare the plotly visualizations
# The path to the data file is `data/covid_cases__vaccination.csv`

def get_cumulative_xy(x, y):
    # https://stackoverflow.com/questions/11352047/finding-moving-average-from-data-points-in-python/34387987#34387987   
    y_cum   = np.cumsum(np.insert(y, 0, 0))
    window_width = 15 # cumulative sum of 15 days
    y_moving_avg = (y_cum[window_width:] - y_cum[:-window_width]) / window_width
    return x[window_width - 1:][280:], y_moving_avg[280:]
#

def get_per_million(df, list_column_names):
    for col in list_column_names:
        new_col = col + '_%'
        df[new_col] = df[col] / df['population']
        df.loc[ df[new_col] > 1, new_col ] = 1
        
        df[new_col] = df[new_col].apply(lambda x: x * 100)
    #
    return df
#

def clean_data( dataset_covid, dataset_population ):
    dfc = pd.read_csv(dataset_covid).drop(['Unnamed: 0'], axis=1)
    dfp = pd.read_csv(dataset_population)

    dfp.rename(columns={ 
        'Country (or dependency)':'country',
        'Population (2020)': 'population',
        'Med. Age': 'median_age' },
        inplace=True
        )

    
    dfp['country'] = dfp.country.str.lower() 

    dfc = dfc.drop( dfc[ dfc.country == "antarctica" ].index )

    lista  = dfp[ ['country', 'population'] ].to_numpy()
    dic    = { e[0] : e[1] for e in lista }
    defdic = defaultdict(lambda:0, dic)
    dfc['population'] = dfc['country'].apply( lambda x: defdic[x] )

    dfc.drop( dfc[ dfc['population'] == 0.0 ].index, inplace=True )
    
    columns = [ 'total_cases', 'total_deaths', 'daily_cases', 'daily_deaths', 'fully_vaccinated', 'daily_people_vaccinated']

    dfc = get_per_million(dfc, columns)

    dfc.drop( columns, axis=1, inplace=True)

    dfc['country'] = dfc.country.str.capitalize() # capitalize country names

    return dfc, dfp
#

def return_figures():
    """Creates plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing plotly visualizations

    """

    dataset_covid      = "data/covid_cases__vaccination.csv"
    dataset_population = "data/population_by_country_2020.csv"

    dfc, dfp = clean_data( dataset_covid, dataset_population )

    dfc_max_vals   = dfc.groupby( ['country'] ).max()
    dic_tot_deaths = dfc_max_vals['total_deaths_%'].sort_values(ascending=False).to_dict()
    countries      = list(dic_tot_deaths.keys())[:10]
    tot_deaths     = list(dic_tot_deaths.values())[:10]

    # first chart plots ...
    
    # graph_one = []    
    # graph_one.append(
    #   go.Scatter(
    #   x = [0, 1, 2, 3, 4, 5],
    #   y = [0, 2, 4, 6, 8, 10],
    #   mode = 'lines'
    #   )
    # )

    graph_one = []
    graph_one.append(
      go.Bar(
      x = countries,
      y = tot_deaths,
      )
    )

    layout_one = dict(title = 'Percentage of deaths to the population',
                # xaxis = dict(title = 'Country'),
                yaxis = dict(title = 'Total deaths'),
                )


    # second chart plots ...

    dic_tot_cases = dfc_max_vals['total_cases_%'].sort_values(ascending=False).to_dict()
    countries      = list(dic_tot_cases.keys())[:10]
    tot_cases      = list(dic_tot_cases.values())[:10]

    graph_two = []
    graph_two.append(
      go.Bar(
      x = countries,
      y = tot_cases,
      )
    )

    layout_two = dict(title = 'Percentage of Covid cases to the population',
                # xaxis = dict(title = 'Country'),
                yaxis = dict(title = 'Total cases'),
                )


# third chart plots ...

    df_peru = dfc[ dfc.country == 'Peru' ].reset_index(drop=True)
    date_list_peru = pd.to_datetime( df_peru.date )
    vacc_list_peru = df_peru['daily_people_vaccinated_%'].to_numpy()
    x_peru_cum, y_peru_cum = get_cumulative_xy(date_list_peru, vacc_list_peru)

    df_ch = dfc[ dfc.country == 'Chile' ].reset_index(drop=True)
    date_list_ch = pd.to_datetime( df_ch.date )
    vacc_list_ch = df_ch['daily_people_vaccinated_%'].to_numpy()
    x_ch_cum, y_ch_cum = get_cumulative_xy(date_list_ch, vacc_list_ch)

    df_nz = dfc[ dfc.country == 'New zealand' ].reset_index(drop=True)
    date_list_nz = pd.to_datetime( df_nz.date )
    vacc_list_nz = df_nz['daily_people_vaccinated_%'].to_numpy()
    x_nz_cum, y_nz_cum = get_cumulative_xy(date_list_nz, vacc_list_nz)

    df_is = dfc[ dfc.country == 'Israel' ].reset_index(drop=True)
    date_list_is = pd.to_datetime( df_is.date )
    vacc_list_is = df_is['daily_people_vaccinated_%'].to_numpy()
    x_is_cum, y_is_cum = get_cumulative_xy(date_list_is, vacc_list_is)

    graph_three = []

    graph_three.append(
      go.Scatter(
      x = x_is_cum,
      y = y_is_cum,
      mode = 'lines',
      name = "Israel",
      )
    )

    graph_three.append(
      go.Scatter(
      x = x_ch_cum,
      y = y_ch_cum,
      mode = 'lines',
      name = "Chile",
      )
    )

    graph_three.append(
      go.Scatter(
      x = x_nz_cum,
      y = y_nz_cum,
      mode = 'lines',
      name = "New Zealand",
      )
    )

    graph_three.append(
      go.Scatter(
      x = x_peru_cum,
      y = y_peru_cum,
      mode = 'lines',
      name = "Peru",
      )
    )




    layout_three = dict(title = 'Percentage of vaccinated population',
                xaxis = dict(title = 'time'),
                yaxis = dict(title = 'people vaccinated')
                       )
    
# fourth chart shows rural population vs arable land
    graph_four = []
    
    graph_four.append(
      go.Scatter(
      x = [20, 40, 60, 80],
      y = [10, 20, 30, 40],
      mode = 'markers'
      )
    )

    layout_four = dict(title = 'Chart Four',
                xaxis = dict(title = 'x-axis label'),
                yaxis = dict(title = 'y-axis label'),
                )
    
    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    # figures.append(dict(data=graph_four, layout=layout_four))

    return figures
#