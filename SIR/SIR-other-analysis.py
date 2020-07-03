# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 14:41:57 2020

@author: ITaylor
"""

region = 'United Kingdom'
def calculate_population_infected(region):
    df = SIR_Cases_vs_Prediction_Short_Term_Lockdown(region)
    population = df.iloc[-1,]['population']
    recovered = df.iloc[-1,]['Recovered_Predict_True']
    pct_infected = recovered / population
    return(pct_infected)


def partner_deaths(region):     
    data = {'Age_Group':['80+','70-79','60-69','50-59','40-49','30-39','20-29','10-19','0-9'],
             'Death_Rate':[x / 100 for x in [14.8, 8, 3.6, 1.3, 0.4, 0.2, 0.2, 0.2, 0.01]],#/100 #Case fatality rate in China https://jamanetwork.com/journals/jama/fullarticle/2762130 - only 1% asymptomatic in this study there was 2.3% death rate
             'Death_Rate_Lower':[x / 100 for x in [13, 7.2, 3.2, 1.1, 0.3, 0.1, 0.1, 0, 0]],
             'Death_Rate_Upper':[x / 100 for x in [16.7, 8.9, 4.0, 1.5, 0.6, 0.4, 0.4, 1, 0.9]],#/100
             'Num_Partners':[33,953,8217,17676,13080,12941,18918,7275,0]}
    
    Age_Deaths = pd.DataFrame(data)
    
    symptomatic = 0.48 # using cruise ship data # in this study ~1.1% death rate https://www.eurosurveillance.org/content/10.2807/1560-7917.ES.2020.25.12.2000256
    
    #From total UK model, how many people end up recovered/ susceptible i.e. how many people were infected. Using ~1% death rate
    #### should be lower than this with social distancing coming in 
    Infected_True_All = calculate_population_infected(region)
    
    Age_Deaths['Deaths_Predicted'] = Age_Deaths.apply(lambda x: x['Num_Partners']*x['Death_Rate']*Infected_True_All*symptomatic, axis=1)
    Age_Deaths['Deaths_Predicted_Upper'] = Age_Deaths.apply(lambda x: x['Num_Partners']*x['Death_Rate_Upper']*Infected_True_All*symptomatic, axis=1)
    Age_Deaths['Deaths_Predicted_Lower'] = Age_Deaths.apply(lambda x: x['Num_Partners']*x['Death_Rate_Lower']*Infected_True_All*symptomatic, axis=1)
    
    Deaths = sum(Age_Deaths['Deaths_Predicted'])
    Deaths_Upper = sum(Age_Deaths['Deaths_Predicted_Upper'])
    Deaths_Lower = sum(Age_Deaths['Deaths_Predicted_Lower'])
    return(Deaths, Deaths_Upper, Deaths_Lower)