"""
Refresh the SIR Regional forecasts
"""

import os
os.chdir('C:/Users/imoge/OneDrive/Documents/GitHub/COVID19/SIR')

#set up
exec(open("SIR-set-up.py").read())

#read in data and format, must run off VPN to access data
exec(open("SIR-prepare-data.py").read())

#set up compartmental model parameters
exec(open("SIR-compartmental-model-parameters.py").read())
    
#functions for plotting SIR model
exec(open("SIR-graphs.py").read())


model_plots('United Kingdom')  

