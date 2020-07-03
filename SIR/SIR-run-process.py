"""
Refresh the SIR Regional forecasts
"""

import os
os.chdir('C:/Users/ITaylor/Desktop/Git/covid-absences/SIR')

#set up
exec(open("SIR-set-up.py").read())

#read in data and format, must run off VPN to access data
exec(open("SIR-prepare-data.py").read())

#set up compartmental model parameters
exec(open("SIR-compartmental-model-parameters.py").read())
    
#functions for plotting SIR model
exec(open("SIR-graphs.py").read())


model_plots('United Kingdom')  

model_plots('France')

model_plots('Italy')



plots_early_lockdown('United Kingdom')

# ### Other analysis
# exec(open("SIR-other-analysis.py").read())
# pct = calculate_population_infected('United Kingdom')
# deaths, deaths_upper, deaths_lower = partner_deaths('United Kingdom')

region = 'Italy'