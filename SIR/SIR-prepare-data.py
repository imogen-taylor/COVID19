"""
Prepare Data
"""

import numpy as np
import optuna
optuna.logging.disable_default_handler()
import pandas as pd
pd.plotting.register_matplotlib_converters()
import io
import requests
from urllib.request import urlopen

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


"""
DATA COMES FROM THE FOLLOWING 
https://coronavirus.data.gov.uk/

download cases csv and deaths csv

"""



"""
Read and Prepare Data from PHE for UK regional level case and death data

"""
#url_c_region = "https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv"
#s_c_region=requests.get(url_c_region).content
#Cases_Region=pd.read_csv(io.StringIO(s_c_region.decode('utf-8')))
#Cases_Region.to_csv('confirmed_regional.csv')
#Cases_Region['Region']=Cases_Region['Area name']
#Cases_Region['Date'] = Cases_Region['Specimen date']
#Cases_Region['Cases'] = Cases_Region['Cumulative lab-confirmed cases']
#Cases_Region = Cases_Region[['Region','Date','Cases']]
#Cases_Region['Date'] = pd.to_datetime(Cases_Region['Date'])
#
#
#url_d_region = "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_deaths_global.csv&filename=time_series_covid19_deaths_global.csv"
#s_d_region=requests.get(url_d_region).content
#Deaths_Region=pd.read_csv(io.StringIO(s_d_region.decode('utf-8')))
#Deaths_Region.to_csv('deaths_regional.csv')
##Deaths_Region = pd.read_csv("coronavirus-deaths.csv")
#Deaths_Region['Region']=Deaths_Region['Country/Region']
#Deaths_Region['Date'] = Deaths_Region['Reporting date']
#Deaths_Region['Deaths'] = Deaths_Region['Cumulative hospital deaths']
#Deaths_Region = Deaths_Region[['Region','Date','Deaths']]
#Deaths_Region['Date'] = pd.to_datetime(Deaths_Region['Date'])
#
#Cases_Region = pd.merge(Cases_Region, Deaths_Region,how='left' ,on=['Region','Date'])


"""
Read and Prepare Data from humdata for global country level cases and deaths
"""

url_c="https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv"
s_c=requests.get(url_c).content
confirmed=pd.read_csv(io.StringIO(s_c.decode('utf-8')))
confirmed.to_csv('confirmed_global.csv')

url_d = "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_deaths_global.csv&filename=time_series_covid19_deaths_global.csv"
s_d=requests.get(url_d).content
deaths=pd.read_csv(io.StringIO(s_d.decode('utf-8')))
deaths.to_csv('deaths_global.csv')

def melt_table(table,var):
    df = pd.melt(table, id_vars =['Country/Region','Province/State']) 
    a = ['Lat','Long']
    df = df[~df.variable.isin(a)]
    df['Date'] = str(0) + df['variable'].astype(str)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y')
    df[var] = df['value']
    df = df[['Country/Region','Province/State','Date',var]]
    return df

c = melt_table(confirmed,'Confirmed')
d = melt_table(deaths,'Deaths')
ncov_df = pd.merge(c, d, how='left', on=['Country/Region','Province/State','Date'])



ncov_df = ncov_df[ncov_df['Country/Region'].isin(countries)]
ncov_df = ncov_df[ncov_df['Province/State'].isnull()]
ncov_df['Region'] = ncov_df['Country/Region']
ncov_df = ncov_df[['Region','Date','Confirmed','Deaths']]

#Group by Region (Country)
ncov_df_grp = ncov_df.groupby(['Region','Date']).sum().reset_index()
ncov_df_grp['Cases'] = ncov_df_grp['Confirmed']

###### moving average
ncov_df_grp['Cases1'] = ncov_df_grp.groupby('Region')['Confirmed'].shift(-roll_shift).fillna(0)
ncov_df_grp['Cases'] = ncov_df_grp.groupby('Region').rolling(roll)['Cases1'].mean().reset_index(drop=True)


# fig = plt.figure(facecolor='w',figsize=(10,4))
# ax = fig.add_subplot(111, axisbelow=True)
# ax.plot(ncov_df_grp[ncov_df_grp['Region']=='United Kingdom']['Date'], ncov_df_grp[ncov_df_grp['Region']=='United Kingdom']['Confirmed'], 'b', alpha=0.5, lw=2, label='Confirmed')#+model_parameters.loc[region,'labels'][0])
# ax.plot(ncov_df_grp[ncov_df_grp['Region']=='United Kingdom']['Date'], ncov_df_grp[ncov_df_grp['Region']=='United Kingdom']['Cases'], 'r', alpha=0.5, lw=2, label='Cases')#+model_parameters.loc[region,'labels'][0])
# ax.set_xlabel('Date')
    
    
#There is limited data on recoveries captured globally, but can use an 
#approximate recovery rate ~14 days
ncov_df_grp = ncov_df_grp.sort_values(['Region','Date'])
ncov_df_grp['Recovered'] = ncov_df_grp.groupby('Region')['Cases'].shift(I).fillna(0)
ncov_df_grp['Infected'] = ncov_df_grp['Cases'] - ncov_df_grp['Recovered']

ncov_df_grp = ncov_df_grp[['Region','Date','Cases','Confirmed','Recovered','Infected','Deaths']]

#There is limited data on recoveries captured globally, but can use an approximate recovery rate ~14 days
Cases_Region = Cases_Region.sort_values(['Region','Date'])
Cases_Region['Recovered'] = Cases_Region.groupby('Region')['Cases'].shift(I).fillna(0)
Cases_Region['Infected'] = Cases_Region['Cases']-Cases_Region['Recovered']
Cases = Cases_Region.append(ncov_df_grp)
Cases['Deaths'] = Cases['Deaths'].fillna(0)

#Estimated true cases today
Cases['Estimated_True_Cases'] = round((Cases['Deaths']/mr)*(2**(v_to_d/dt)))
Cases['Estimated_True_Recovered'] = Cases.groupby('Region')['Estimated_True_Cases'].shift(I).fillna(0) #- Cases['Deaths']
Cases['Estimated_True_Infected'] = Cases['Estimated_True_Cases'] - Cases['Estimated_True_Recovered'] #- Cases['Deaths']
Cases['True_Confirmed_Ratio'] = Cases[['Estimated_True_Cases','Cases']].apply(lambda x: np.nan if x[1]==0 else x[0]/x[1], axis=1)

Cases = Cases[Cases['Cases']>0]
Cases = Cases[Cases['Date']<today_mroll]
mddate = max(Cases['Date'])

data_cols = ["Infected", "Deaths", "Recovered"]
ncov_df["Date"] = pd.to_datetime(ncov_df["Date"], format='%m/%d/%y')
ncov_df["Country"] = ncov_df["Region"]
ncov_df['Province'] = ncov_df['Region']
ncov_df['Recovered'] = ncov_df.groupby('Region')['Confirmed'].shift(I).fillna(0)
ncov_df["Infected"] = ncov_df["Confirmed"] - ncov_df["Deaths"] - ncov_df["Recovered"]
ncov_df[data_cols] = ncov_df[data_cols].astype(np.int64)
ncov_df = ncov_df.loc[:, ["Date", "Country", "Province", *data_cols]]
ncov_df.tail()

Cases["Country"] = Cases["Region"].replace(
    {
     "London": "United Kingdom",
     "North West": "United Kingdom",
     "North East and Yorkshire": "United Kingdom",
     "South West": "United Kingdom",
     "South East": "United Kingdom",
     "Midlands": "United Kingdom",
     "East of England": "United Kingdom",
     "England ": "United Kingdom",
     "Wales": "United Kingdom",
     "Scotland": "United Kingdom",
     "Northern Ireland": "United Kingdom"
     })

end_date = pd.to_datetime("2020-12-01").date()

Cases.to_csv("Cases.csv")