# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 16:47:46 2020

@author: ITaylor
"""
"""
What is SIR model?
SIR model is a simple mathematical model to understand outbreak of infectious diseases.
The SIR epidemic model - Learning Scientific Programming with Python
S: Susceptible (=All - Confirmed)
I: Infected (=Confirmed - Recovered - Deaths)
R: Recovered or fatal (=Recovered + Deaths)
Note: THIS IS NOT THE GENERAL MODEL! Though R in SIR model is "Recovered and have immunity", I defined "R as Recovered or fatal". This is because mortality rate cannot be ignored in the real COVID-19 data.

Model:
S + I ⟶β 2I I ⟶γ R

β : Effective contact rate [1/min]
γ : Recovery(+Mortality) rate [1/min]
Ordinary Differential Equation (ODE):
dSdt = -beta * S * I / N
dIdt = beta * S * I / N - gamma * I
dRdt = gamma * I
Where N=S+I+R is the total population, T is the elapsed time from the start date.

Now use this try to fit a model for each region of UK
Parameters taken from existing papers
"""

def SIR_Prediction(region):
        
    N, P, f = Population_parameters(region)
    # Initial number of infected and recovered individuals, I0 and R0.
    R0 = 0
    if max(Cases['Country']==region):
        I0 = 1
    else: 
        I0 = min(Cases[(Cases['Region']==region) & (Cases['Cases']>0)]['Cases'])
    # Everyone else, S0, is susceptible to infection initially.
    S0 = N - I0 - R0
       
    # Contact rate, beta, and mean recovery rate, gamma, (in 1/days).
    beta = model_parameters[model_parameters['Region']==region]['beta0'].item()
    gamma = model_parameters[model_parameters['Region']==region]['gamma'].item()

    start_date = min(Cases[Cases['Region']==region]['Date']).date()

    diff = (end_date - start_date).days
    # A grid of time points (in days)
    t = np.linspace(0, diff, diff+1)
    
    # The SIR model differential equations.
    def deriv(y, t, N, beta, gamma):
        S, I, R = y        
        dSdt = -beta * S * I / N
        dIdt = beta * S * I / N - gamma * I
        dRdt = gamma * I
        return dSdt, dIdt, dRdt

    # Initial conditions vector
    y0 = S0, I0, R0
    # Integrate the SIR equations over the time grid, t.
    ret = odeint(deriv, y0, t, args=(N, beta, gamma))
    S, I, R = ret.T
       
    Predicted = pd.DataFrame(data={'time': t, 
                                    'Susceptible_Predict': S,
                                    'Infected_Predict': I,
                                    'Recovered_Predict': R}).round()
    Predicted['Date'] = pd.date_range(start=start_date, periods=len(Predicted))
    min_start_date = min(Cases['Date']).date()
    
    Date_Range = pd.DataFrame()
    Date_Range['Date'] = pd.date_range(start=min_start_date, periods=diff)
    Predicted = pd.merge(Date_Range, Predicted, how='left', on='Date')
    Predicted['Susceptible_Predict'] = Predicted['Susceptible_Predict'].fillna(S0).astype(int)
    Predicted['Infected_Predict'] = Predicted['Infected_Predict'].fillna(0).astype(int)
    Predicted['Recovered_Predict'] = Predicted['Recovered_Predict'].fillna(0).astype(int)
    Predicted['Susceptible_Predict_True'] = round(Predicted['Susceptible_Predict']*f).astype(int)
    Predicted['Infected_Predict_True'] = round(Predicted['Infected_Predict']*f).astype(int)
    Predicted['Recovered_Predict_True'] = round(Predicted['Recovered_Predict']*f).astype(int)
    return(Predicted)

def SIR_Cases_vs_Prediction_Short_Term(region):
    Predicted = SIR_Prediction(region)
    N, P, f = Population_parameters(region)
    
    Region_Cases = Cases[(Cases['Region']==region)]
    Region_Cases['Cases'] = Region_Cases['Cases'].fillna(0).astype(float)

    Region_df_td = pd.merge(Predicted, Region_Cases, how='left', on='Date')
    #Region_df_td = Region_df[(Region_df['Date'] < today) & (Region_df['Date']>='2020-03-10')]    
    Region_df_td['population'] = P
    Region_df_td['Region'] = region
    Region_df_td['Cases_Norm'] = Region_df_td['Cases']/P
    Region_df_td['Infected_Predict_Norm'] = Region_df_td['Infected_Predict']/P
    Region_df_td['Recovered_Predict_Norm'] = Region_df_td['Recovered_Predict']/P
    Region_df_td['Susceptible_Predict_Norm'] = Region_df_td['Susceptible_Predict']/P
    Region_df_td['Infected_Predict_True_Norm'] = Region_df_td['Infected_Predict_True']/P
    Region_df_td['Recovered_Predict_True_Norm'] = Region_df_td['Recovered_Predict_True']/P
    Region_df_td['Susceptible_Predict_True_Norm'] = Region_df_td['Susceptible_Predict_True']/P
    
    return(Region_df_td)

def SIR_Prediction_Plot(region):
    Predicted = SIR_Prediction(region)
    N, P, f = Population_parameters(region)
    
    fig = plt.figure(facecolor='w')
    ax = fig.add_subplot(111, axisbelow=True)
    ax.plot(Predicted['Date'], Predicted['Susceptible_Predict_True']/P, 'b', alpha=0.5, lw=2, label='Susceptible')
    ax.plot(Predicted['Date'], Predicted['Infected_Predict_True']/P, 'r', alpha=0.5, lw=2, label='Infected')
    ax.plot(Predicted['Date'], Predicted['Recovered_Predict_True']/P, 'g', alpha=0.5, lw=2, label='Recovered with Immunity')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number (Proportion of Population)')
    ax.set_ylim(0,1.1)
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_minor_locator(days)
    ax.set_title(label='Predicted (Estimated) True Cases : '+region)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
    plt.show()
    
def SIR_Cases_vs_Prediction_Short_Term_Plot(region):
    Region_df = SIR_Cases_vs_Prediction_Short_Term(region)
    Region_df1 = Region_df[(Region_df['Date']<today_7) & (Region_df['Date']>=today_m14)]
    
    #Plot actual confirmed vs predicted
    X=max(Region_df1['Infected_Predict'].fillna(0))
    # Plot the data on three separate curves for S(t), I(t) and R(t)
    fig = plt.figure(facecolor='w',figsize=(10,4))
    ax = fig.add_subplot(111, axisbelow=True)
    #plot % of total population who are predicted to be a confirmed case
    ax.plot(Region_df1['Date'], Region_df1['Susceptible_Predict'], 'b', alpha=0.5, lw=2, label='Susceptible')
    ax.plot(Region_df1['Date'], Region_df1['Infected_Predict'], 'r', alpha=0.5, lw=2, label='Infected')
    ax.plot(Region_df1['Date'], Region_df1['Recovered_Predict'], 'g', alpha=0.5, lw=2, label='Recovered with immunity')
    ax.plot(Region_df1['Date'], Region_df1['Infected'], 'y', alpha=0.5, lw=2, label='Infected Actual' )
    #ax.plot(Region_df1['Date'], Region_df1['Cases'], 'm', alpha=0.5, lw=2, label='Cases Actual' )
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Cases')
    ax.set_ylim(0,(1.1*X))
    ax.yaxis.set_tick_params(length=0)
    ax.set_title(label='Predicted vs Actual Confirmed Cases : '+region)
    #ax.xaxis.set_tick_params(length=0)
    ax.xaxis.set_minor_locator(days)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
    plt.show()



############################################################################
def SIR_Prediction_Soft_Lockdown(region):
    soft_lockdown_dt = Soft_Lockdown_Dates(region) + timedelta(days=dorm)
    Predicted = SIR_Prediction(region)
    N, P, f = Population_parameters(region)
    Predicted0 = Predicted[Predicted['Date']<soft_lockdown_dt]
    
    # Initial number of infected and recovered individuals, I0 and R0.
    S0 = Predicted[Predicted['Date']==soft_lockdown_dt]['Susceptible_Predict'].item()
    I0 = Predicted[Predicted['Date']==soft_lockdown_dt]['Infected_Predict'].item()
    R0 = Predicted[Predicted['Date']==soft_lockdown_dt]['Recovered_Predict'].item()
    
    N = S0 + I0 + R0
    # Contact rate, beta, and mean recovery rate, gamma, (in 1/days).
    beta = model_parameters[model_parameters['Region']==region]['beta1'].item() ###post lockdown R0
    gamma = model_parameters[model_parameters['Region']==region]['gamma'].item()
    start_date = soft_lockdown_dt

    diff = (end_date - start_date.date()).days
    # A grid of time points (in days)
    t = np.linspace(0, diff, diff+1)
    
    # The SIR model differential equations.
    def deriv(y, t, N, beta, gamma):
        S, I, R = y        
        dSdt = -beta * S * I / N
        dIdt = beta * S * I / N - gamma * I
        dRdt = gamma * I
        return dSdt, dIdt, dRdt

    # Initial conditions vector
    y0 = S0, I0, R0
    # Integrate the SIR equations over the time grid, t.
    ret = odeint(deriv, y0, t, args=(N, beta, gamma))
    S, I, R = ret.T
       
    Predicted1 = pd.DataFrame(data={'time': t, 
                                    'Susceptible_Predict': S,
                                    'Infected_Predict': I,
                                    'Recovered_Predict': R}).round()
    Predicted1['Date'] = pd.date_range(start=start_date, periods=len(Predicted1))
    
    Date_Range = pd.DataFrame()
    Date_Range['Date'] = pd.date_range(start=start_date, periods=diff)
    Predicted1 = pd.merge(Date_Range, Predicted1, how='left', on='Date')
    Predicted1['Susceptible_Predict'] = Predicted1['Susceptible_Predict'].fillna(S0).astype(int)
    Predicted1['Infected_Predict'] = Predicted1['Infected_Predict'].fillna(0).astype(int)
    Predicted1['Recovered_Predict'] = Predicted1['Recovered_Predict'].fillna(0).astype(int)
    Predicted1['Susceptible_Predict_True'] = round(Predicted1['Susceptible_Predict']*f).astype(int)
    Predicted1['Infected_Predict_True'] = round(Predicted1['Infected_Predict']*f).astype(int)
    Predicted1['Recovered_Predict_True'] = round(Predicted1['Recovered_Predict']*f).astype(int)
    
    Predicted = Predicted0.append(Predicted1)
    
    return(Predicted)



def SIR_Prediction_Lockdown(region):
    if region == 'United Kingdom':
        lockdown_dt = Lockdown_Dates(region) + timedelta(days=dorm)
        Predicted = SIR_Prediction_Soft_Lockdown(region)
    elif region in ('Italy','France'):
        lockdown_dt = Lockdown_Dates(region) + timedelta(days=dorm)
        Predicted = SIR_Prediction_Lockdown(region)
        
    N, P, f = Population_parameters(region)
    Predicted0 = Predicted[Predicted['Date']<lockdown_dt]
    
    # Initial number of infected and recovered individuals, I0 and R0.
    S0 = Predicted[Predicted['Date']==lockdown_dt]['Susceptible_Predict'].item()
    I0 = Predicted[Predicted['Date']==lockdown_dt]['Infected_Predict'].item()
    R0 = Predicted[Predicted['Date']==lockdown_dt]['Recovered_Predict'].item()
    
    N = S0 + I0 + R0
    # Contact rate, beta, and mean recovery rate, gamma, (in 1/days).
    beta = model_parameters[model_parameters['Region']==region]['beta2'].item() ###post lockdown R0
    gamma = model_parameters[model_parameters['Region']==region]['gamma'].item()
    start_date = lockdown_dt
    

    diff = (end_date - start_date.date()).days
    # A grid of time points (in days)
    t = np.linspace(0, diff, diff+1)
    
    # The SIR model differential equations.
    def deriv(y, t, N, beta, gamma):
        S, I, R = y        
        dSdt = -beta * S * I / N
        dIdt = beta * S * I / N - gamma * I
        dRdt = gamma * I
        return dSdt, dIdt, dRdt

    # Initial conditions vector
    y0 = S0, I0, R0
    # Integrate the SIR equations over the time grid, t.
    ret = odeint(deriv, y0, t, args=(N, beta, gamma))
    S, I, R = ret.T
       
    Predicted1 = pd.DataFrame(data={'time': t, 
                                    'Susceptible_Predict': S,
                                    'Infected_Predict': I,
                                    'Recovered_Predict': R}).round()
    Predicted1['Date'] = pd.date_range(start=start_date, periods=len(Predicted1))
    
    Date_Range = pd.DataFrame()
    Date_Range['Date'] = pd.date_range(start=start_date, periods=diff)
    Predicted1 = pd.merge(Date_Range, Predicted1, how='left', on='Date')
    Predicted1['Susceptible_Predict'] = Predicted1['Susceptible_Predict'].fillna(S0).astype(int)
    Predicted1['Infected_Predict'] = Predicted1['Infected_Predict'].fillna(0).astype(int)
    Predicted1['Recovered_Predict'] = Predicted1['Recovered_Predict'].fillna(0).astype(int)
    Predicted1['Susceptible_Predict_True'] = round(Predicted1['Susceptible_Predict']*f).astype(int)
    Predicted1['Infected_Predict_True'] = round(Predicted1['Infected_Predict']*f).astype(int)
    Predicted1['Recovered_Predict_True'] = round(Predicted1['Recovered_Predict']*f).astype(int)
    
    Predicted = Predicted0.append(Predicted1)
    
    return(Predicted)

def SIR_Cases_vs_Prediction_Short_Term_Lockdown(region):
    Predicted = SIR_Prediction_Lockdown(region)
    N, P, f = Population_parameters(region)
    
    Region_Cases = Cases[(Cases['Region']==region)]
    Region_Cases['Cases'] = Region_Cases['Cases'].fillna(0).astype(float)

    Region_df_td = pd.merge(Predicted, Region_Cases, how='left', on='Date')
    #Region_df_td = Region_df[(Region_df['Date'] < today) & (Region_df['Date']>='2020-03-10')]    
    Region_df_td['population'] = P
    Region_df_td['Region'] = region
    Region_df_td['Cases_Norm'] = Region_df_td['Cases']/P
    Region_df_td['Infected_Predict_Norm'] = Region_df_td['Infected_Predict']/P
    Region_df_td['Recovered_Predict_Norm'] = Region_df_td['Recovered_Predict']/P
    Region_df_td['Susceptible_Predict_Norm'] = Region_df_td['Susceptible_Predict']/P
    Region_df_td['Infected_Predict_True_Norm'] = Region_df_td['Infected_Predict_True']/P
    Region_df_td['Recovered_Predict_True_Norm'] = Region_df_td['Recovered_Predict_True']/P
    Region_df_td['Susceptible_Predict_True_Norm'] = Region_df_td['Susceptible_Predict_True']/P
    
    return(Region_df_td)

def SIR_Prediction_Lockdown_Plot(region):
    Predicted = SIR_Prediction(region)
    Predicted_L = SIR_Prediction_Lockdown(region)
    N, P, f = Population_parameters(region)
    
    fig = plt.figure(facecolor='w',figsize=(10,4))
    ax = fig.add_subplot(111, axisbelow=True)
    ax.plot(Predicted['Date'], Predicted['Susceptible_Predict_True']/P, 'b', alpha=0.5, lw=2, ls = '--', label='Susceptible - Original')
    ax.plot(Predicted['Date'], Predicted['Infected_Predict_True']/P, 'r', alpha=0.5, lw=2, ls = '--', label='Infected - Original')
    ax.plot(Predicted['Date'], Predicted['Recovered_Predict_True']/P, 'g', alpha=0.5, lw=2, ls = '--', label='Recovered/Deaths - Original')
    ax.plot(Predicted_L['Date'], Predicted_L['Susceptible_Predict_True']/P, 'b', alpha=0.5, lw=2, label='Susceptible - Lockdown Forecast')
    ax.plot(Predicted_L['Date'], Predicted_L['Infected_Predict_True']/P, 'r', alpha=0.5, lw=2, label='Infected - Lockdown Forecast')
    ax.plot(Predicted_L['Date'], Predicted_L['Recovered_Predict_True']/P, 'g', alpha=0.5, lw=2, label='Recovered/Deaths - Lockdown Forecast')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number (Proportion of Population)')
    ax.set_ylim(0,1.1)
    ax.axvline(today, 0, 1, color='k', alpha=0.5, lw=2, ls = ':', label='today')
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_minor_locator(days)
    ax.set_title(label='Predicted (Estimated) True Cases & Lockdown : '+region)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend(loc='center right')
    legend.get_frame().set_alpha(0.5)
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
    plt.show()

def SIR_Cases_vs_Prediction_Short_Term_Lockdown_Plot(region):
    Region_df = SIR_Cases_vs_Prediction_Short_Term_Lockdown(region)
    Region_df1 = Region_df[(Region_df['Date']<today_7) & (Region_df['Date']>=today_m14)]
    
    #Plot actual confirmed vs predicted
    X=max(Region_df1['Infected_Predict'].fillna(0))
    # Plot the data on three separate curves for S(t), I(t) and R(t)
    fig = plt.figure(facecolor='w',figsize=(10,4))
    ax = fig.add_subplot(111, axisbelow=True)
    #plot % of total population who are predicted to be a confirmed case
    ax.plot(Region_df1['Date'], Region_df1['Susceptible_Predict'], 'b', alpha=0.5, lw=2, label='Susceptible')
    ax.plot(Region_df1['Date'], Region_df1['Infected_Predict'], 'r', alpha=0.5, lw=2, label='Infected')
    ax.plot(Region_df1['Date'], Region_df1['Recovered_Predict'], 'g', alpha=0.5, lw=2, label='Recovered with immunity')
    ax.plot(Region_df1['Date'], Region_df1['Infected'], 'y', alpha=0.5, lw=2, label='Infected Actual' )
    #ax.plot(Region_df1['Date'], Region_df1['Cases'], 'm', alpha=0.5, lw=2, label='Cases Actual' )
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Cases')
    ax.set_ylim(0,(1.1*X))
    ax.yaxis.set_tick_params(length=0)
    ax.set_title(label='Predicted vs Actual Confirmed Cases : '+region)
    #ax.xaxis.set_tick_params(length=0)
    ax.xaxis.set_minor_locator(days)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)
    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)
    plt.show()    

       
def model_plots(region):
    #SIR_Prediction_Plot(region)
    #SIR_Cases_vs_Prediction_Short_Term_Plot(region)
    SIR_Prediction_Lockdown_Plot(region)
    SIR_Cases_vs_Prediction_Short_Term_Lockdown_Plot(region)

#region = 'United Kingdom'
def SIR_data(region):
    Region_df = SIR_Cases_vs_Prediction_Short_Term(region)
    Region_df_Lockdown = SIR_Cases_vs_Prediction_Short_Term_Lockdown(region)
    return(Region_df)