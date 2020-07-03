
from datetime import timedelta
import os
import matplotlib.pyplot as plt
import numpy as np
import optuna
optuna.logging.disable_default_handler()
import pandas as pd
pd.plotting.register_matplotlib_converters()
from scipy.integrate import odeint
from sklearn.metrics import mean_squared_error
import matplotlib.dates as mdates
import io
import requests
import xlrd 
from urllib.request import urlopen

I = 10 #average days to recovery 
v_to_d = 17.3 #Average time from symptom onset to death - china averages
dt = 6.18 #Average time for cases to double - global averages, also similar to current UK trend
mr = 0.0087 #Mortality Rate
dorm = 14 #5 days from infected to symptomatic + 3 days for testing(delay of lockdown to slowing of cases)

countries = ['United Kingdom','Italy','France','Spain']

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

today = pd.to_datetime('today').floor('D') #date.today()
today_m1 = pd.to_datetime('today').floor('D') - timedelta(days=1)
today_7 = pd.to_datetime('today').floor('D') + timedelta(days=7)
today_m14 = pd.to_datetime('today').floor('D') - timedelta(days=28)
days = mdates.DayLocator()  # every month
