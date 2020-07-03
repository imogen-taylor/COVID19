
"""
Set model parameters, these are taken from known parameters

"""

def dtf(date):
    date = pd.to_datetime(date, format='%m/%d/%y')
    return(date)
    
if I == 10:
    model_parameters = pd.DataFrame(data={'Region': ['United Kingdom', 'France', 'Italy'], 
                                      'population': [67784927,65234791,60485231],
                                       'beta': [[0.26,0.22,0.135,0.14,0.15,0.17], [0.27,0.15], [0.30,0.14]],
                                       'date': [[dtf("03/13/20"),dtf("03/23/20"),dtf("05/13/20"),dtf("06/01/20"),dtf("06/14/20")],[dtf("03/17/20")],[dtf("03/09/20")]],
                                       #'beta': [[0.27,0.23,0.155,0.27], [0.26,0.16], [0.32,0.12]],
                                       #'date': [[dtf("03/13/20"),dtf("03/23/20"),dtf("04/21/20")],[dtf("03/17/20")],[dtf("03/09/20")]],
                                      'labels': [['Pre-Lockdown','Soft Lockdown', 'Lockdown','2 People Meeting Outdoors','6 People Meeting Outdoors','Shops Opening'],['Pre-Lockdown','Lockdown'],['Pre-Lockdown','Lockdown']],
                                      'dorm':[16,14,14]}
                                     )
model_parameters['gamma']=1/I
model_parameters=model_parameters.set_index('Region')

def Population_parameters(region):
    #Set suceptible population
    f = Cases[(Cases['Region']==region) & (Cases['Date']==mddate)]['True_Confirmed_Ratio'].item()
    P = model_parameters.loc[region,'population']
    N = P/f
    return(N,P,f)

