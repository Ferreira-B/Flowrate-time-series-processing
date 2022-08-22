import datetime
import math
import numpy as np
import pandas as pd
# import pmdarima as pm
# from joblib import Parallel
# from joblib import delayed
from multiprocessing import cpu_count
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from pandas.api.types import CategoricalDtype
from math import sqrt
from sklearn.metrics import mean_squared_error
from scipy.optimize import minimize
from statsmodels.tsa.holtwinters import SimpleExpSmoothing


class ARIMA_QV:
    """Scikit-learn like interface for Holt-Winters method."""

    def __init__(self, a1=0.5, a2=0.1, a3=0.5, a4=0.5):
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4

    def fit(self, series):
        # note that unlike scikit-learn's fit method, it doesn't learn
        # the optimal model paramters, alpha, beta, gamma instead it takes
        # whatever the value the user specified the produces the predicted time
        # series, this of course can be changed.

        a1 = self.a1
        a2 = self.a2
        a3 = self.a3
        a4 = self.a4

        self.series = series

        ####

        b1 = a1 - (2*math.cos(2*math.pi/7)+1)
        b2 = a2 - (2*math.cos(2*math.pi/7)+1)*a1 + 2 * math.cos(2*math.pi/7)+1
        b3 = a3 - (2*math.cos(2*math.pi/7)+1)*a2 + \
            (2 * math.cos(2*math.pi/7)+1)*a1-1
        b4 = a4 - (2*math.cos(2*math.pi/7)+1)*a3 + \
            (2 * math.cos(2*math.pi/7)+1)*a2-a1
        b5 = -(2*math.cos(2*math.pi/7)+1)*a4 + \
            (2*math.cos(2*math.pi/7)+1)*a3-a2
        b6 = (2*math.cos(2*math.pi/7)+1)*a4-a3
        b7 = -a4

        predictions = []
        [predictions.append(None) for i in range(7)]

        for i in range(7, len(series)):

            f = - b1 * series[i-1] - b2 * series[i-2] - b3 * series[i-3] - b4 * \
                series[i-4] - b5 * series[i-5] - \
                b6 * series[i-6] - b7 * series[i-7]
            predictions.append(f)

            # print()
        self.predictions_ = predictions
        return self

    def predict(self, n_preds=1):

        series = self.series
        predictions = self.predictions_

        a1 = self.a1
        a2 = self.a2
        a3 = self.a3
        a4 = self.a4

        ####

        b1 = a1 - (2*math.cos(2*math.pi/7)+1)
        b2 = a2 - (2*math.cos(2*math.pi/7)+1)*a1 + 2 * math.cos(2*math.pi/7)+1
        b3 = a3 - (2*math.cos(2*math.pi/7)+1)*a2 + \
            (2 * math.cos(2*math.pi/7)+1)*a1-1
        b4 = a4 - (2*math.cos(2*math.pi/7)+1)*a3 + \
            (2 * math.cos(2*math.pi/7)+1)*a2-a1
        b5 = -(2*math.cos(2*math.pi/7)+1)*a4 + \
            (2*math.cos(2*math.pi/7)+1)*a3-a2
        b6 = (2*math.cos(2*math.pi/7)+1)*a4-a3
        b7 = -a4

        i = len(series)

        f = - b1 * series[i-1] - b2 * series[i-2] - b3 * series[i-3] - b4 * \
            series[i-4] - b5 * series[i-5] - \
            b6 * series[i-6] - b7 * series[i-7]

        predictions.append(f)

        return predictions


def timeseries_cv_score(params, series):
    a1, a2, a3, a4 = params

    model = ARIMA_QV(a1, a2, a3, a4)
    model.fit(series)
    predictions = model.predictions_

    rmse = measure_rmse(series[7:], predictions[7:])
    return rmse


def sarima_configs(p_min, p_max, q_min, q_max,
                   P_min, P_max, Q_min, Q_max):
    models = list()
    # define config lists
    p_params = range(p_min, p_max + 1)
    q_params = range(q_min, q_max + 1)
    t_params = ['n', 'c', 't', 'ct']
    P_params = range(P_min, P_max + 1)
    Q_params = range(Q_min, Q_max + 1)
    # create config instances
    for p in p_params:
        for q in q_params:
            for t in t_params:
                for P in P_params:
                    for Q in Q_params:
                        cfg = [(p, 0, q), (P, 0, Q, 0), t]
                        models.append(cfg)

    return models


def grid_search(history, cfg_list, parallel=True):

	scores = None
	if parallel:
		# execute configs in parallel
		executor = Parallel(n_jobs=cpu_count(), backend='multiprocessing')
		tasks = (delayed(sarima_run)(history, cfg) for cfg in cfg_list)
		scores = executor(tasks)
	else:
		scores = [sarima_run(history, cfg) for cfg in cfg_list]

	scores = list(scores)

	# remove empty results
	scores = [r for r in scores if r[1] != None]

    #turn AIC values into positives
	for r in scores:
		r[1] = abs(r[1])

	# sort configs by error, asc
	scores.sort(key=lambda tup: tup[1])

	return scores


def sarima_run(history, cfg):
    # print('## testing row ', cfg)
    aic = None
    bic = None
    order, sorder, trend = cfg
    try:
            # define model
        model = ARIMA(endog=history, order=order, seasonal_order=sorder,
                      trend=trend, enforce_stationarity=False, enforce_invertibility=False)
        # fit model
        model_fit = model.fit()
        aic = model_fit.aic
        bic = model_fit.bic

    except:
    	print('Error in ', cfg)
    	# continue

    return [cfg, aic]


def measure_rmse(test, predicted):
	return sqrt(mean_squared_error(test, predicted))


def Quevedo(hist, type_analysis, date1):
    # print(date1)
    #Ficheiro com feriados
    holiday = pd.read_csv("Holidays.csv", header=0)
    # print(holiday)
    # print(date1)
    ###################################


    values_h = hist['value']
    dates_h = hist['date']
    spacing = (dates_h.iloc[1] - dates_h.iloc[0])

    ###Estimar o periodo de um dia, ou seja, o nr de medições que ocorrem num dia
    ###Como o 1º dia do historico pode vir incompleto, vamos buscar a contagem do 2 dia
    hist.index = hist['date']
    hist.index = pd.to_datetime(hist.index)
    history_count_day = hist.groupby(hist.index.date).count()
    period_estimate = history_count_day.iloc[1].value
    # hist.drop(hist.tail(period_estimate).index, inplace=True)

    del hist['date']

    ### Quantas medições ocorrem numa hora
    N = 24 / period_estimate

    #agregado diário
    history_sum_day = hist.groupby(hist.index.date).sum()

    #correção do N
    for idx, day in enumerate(history_sum_day.value):
        history_sum_day.iloc[idx] = history_sum_day.iloc[idx] * N

    # print('History_sum_day \n', history_sum_day)
    #############

    holiday = holiday['date']
    holiday = [np.datetime64(x) for x in holiday]

    hol = 0
    last_day = date1

    if last_day in holiday:
        hol = 1

    if type_analysis == 'original' and hol == 0:
        x = [0.6, 0.5, 0.6, 0.5]
        data = history_sum_day[1:].values
        data = [item for sublist in data for item in sublist]

        opt = minimize(timeseries_cv_score, x0=x,
                       args=(data),
                       method='TNC')

        # print('original parameters: {}'.format(str(x)))
        # print('best parameters: {}'.format(str(opt.x)))

        # print('end')

        a1, a2, a3, a4 = opt.x
        model = ARIMA_QV(a1, a2, a3, a4)
        model.fit(data)

        predictions = model.predict(n_preds=1)

    elif type_analysis == 'grid' and hol == 0:

        #### Grid Search
        p_min = 0
        p_max = 3

        q_min = 0
        q_max = 3

        P_min = 0
        P_max = 1

        Q_min = 0
        Q_max = 1

        cfg_list = sarima_configs(p_min, p_max, q_min, q_max,
                                  P_min, P_max, Q_min, Q_max)

        # print('Total de: ', len(cfg_list), ' combinações')

        combinations = grid_search(history_sum_day, cfg_list, parallel=False)
        # print(combinations)
        # print(combinations[0][0])
        order, sorder, trend = combinations[0][0]

        #1day forecast
        mod = ARIMA(endog=history_sum_day, order=order, seasonal_order=sorder,
                    trend=trend, enforce_stationarity=False, enforce_invertibility=False)

        res = mod.fit()

        predictions = res.forecast(
            steps=len(history_sum_day), alpha=0.05).values

    else:
        # print('É feriado')

        #get all the sundays
        sundays = history_sum_day.copy()
        sundays = sundays.reset_index()
        sundays['index'] = pd.to_datetime(sundays['index'])
        sundays['weekday'] = sundays['index'].dt.dayofweek
        # print(sundays)
        sundays = sundays.loc[sundays['weekday'] == 6]
        # print(sundays)
        sundays = sundays.reset_index(drop=True)
        del sundays['weekday']
        vals = sundays['value'].values

        model = SimpleExpSmoothing(vals)
        model_fit = model.fit()
        predictions = model_fit.predict(len(vals), len(vals))

        # print(predictions)

    # plt.figure(1)
    # plt.plot(history_sum_day.index, history_sum_day.values,'b.-', label='Histórico')
    # plt.plot(history_sum_day.index[:-1], predictions[:-1], 'g.-', label='Fit')
    # plt.plot(history_sum_day.index[-1], predictions[-1], 'r.-', label='Forcasted')
    # plt.legend()
    # rmse = history_sum_day.values[-1]-predictions[-1]
    # plt.title(label='ARIMA for daily forecast // SE= ' + str(round(rmse[0], 2)))

    #######Pattern
    hist['date'] = hist.index
    hist['weekday'] = hist['date'].apply(lambda x: x.weekday())
    # print('hist with weekday \n', hist)









    ####Aplicar o padrão ao novo dia

    new_day = predictions[-1]
    new_day_wd = date1.astype(datetime.datetime).isoweekday()
    # print(new_day_wd,hol)
    pat = None
    ################
    # plt.figure(2)
    if new_day_wd < 6 and hol == 0:
        ###weekday
        weekdays_only = hist[hist['weekday'] < 5]
        del weekdays_only['weekday']
        del weekdays_only['date']
        # print('weekday only \n', weekdays_only)
        weekdays_only_patt = weekdays_only.groupby(weekdays_only.index.time).mean()
        # print('weekday only patt mean \n', weekdays_only_patt)
        sum_wd_patt = weekdays_only_patt.sum()
        # print(sum_wd_patt)
        for i in range(len(weekdays_only_patt)):
            weekdays_only_patt.iloc[i] = weekdays_only_patt.iloc[i] / sum_wd_patt
        # print('weekday only patt \n', weekdays_only_patt)


        pat = weekdays_only_patt
        for i in range(len(pat)):
            pat.iloc[i] = pat.iloc[i] * new_day / N
        
        # plt.plot(weekdays_only_patt, label='Weekdays')

    # if new_day_wd == 1 and hol == 0:
    #     ###Monday
    #     weekdays_only = hist[hist['weekday'] == 1]
    #     del weekdays_only['weekday']
    #     del weekdays_only['date']
    #     # print('weekday only \n', weekdays_only)
    #     weekdays_only_patt = weekdays_only.groupby(weekdays_only.index.time).mean()
    #     # print('weekday only patt mean \n', weekdays_only_patt)
    #     sum_wd_patt = weekdays_only_patt.sum()
    #     # print(sum_wd_patt)
    #     for i in range(len(weekdays_only_patt)):
    #         weekdays_only_patt.iloc[i] = weekdays_only_patt.iloc[i] / sum_wd_patt
    #     # print('weekday only patt \n', weekdays_only_patt)


    #     pat = weekdays_only_patt
    #     for i in range(len(pat)):
    #         pat.iloc[i] = pat.iloc[i] * new_day / N
        
    #     plt.plot(weekdays_only_patt, label='Monday')

    # elif new_day_wd == 2 and hol == 0:
    #     ###Thuesday
    #     weekdays_only = hist[hist['weekday'] == 2]
    #     del weekdays_only['weekday']
    #     del weekdays_only['date']
    #     # print('weekday only \n', weekdays_only)
    #     weekdays_only_patt = weekdays_only.groupby(weekdays_only.index.time).mean()
    #     # print('weekday only patt mean \n', weekdays_only_patt)
    #     sum_wd_patt = weekdays_only_patt.sum()
    #     # print(sum_wd_patt)
    #     for i in range(len(weekdays_only_patt)):
    #         weekdays_only_patt.iloc[i] = weekdays_only_patt.iloc[i] / sum_wd_patt
    #     # print('weekday only patt \n', weekdays_only_patt)


    #     pat = weekdays_only_patt
    #     for i in range(len(pat)):
    #         pat.iloc[i] = pat.iloc[i] * new_day / N
        
    #     plt.plot(weekdays_only_patt, label='Thuesday')

    # elif new_day_wd == 3 and hol == 0:
    #     ###Wednesday
    #     weekdays_only = hist[hist['weekday'] == 3]
    #     del weekdays_only['weekday']
    #     del weekdays_only['date']
    #     # print('weekday only \n', weekdays_only)
    #     weekdays_only_patt = weekdays_only.groupby(weekdays_only.index.time).mean()
    #     # print('weekday only patt mean \n', weekdays_only_patt)
    #     sum_wd_patt = weekdays_only_patt.sum()
    #     # print(sum_wd_patt)
    #     for i in range(len(weekdays_only_patt)):
    #         weekdays_only_patt.iloc[i] = weekdays_only_patt.iloc[i] / sum_wd_patt
    #     # print('weekday only patt \n', weekdays_only_patt)


    #     pat = weekdays_only_patt
    #     for i in range(len(pat)):
    #         pat.iloc[i] = pat.iloc[i] * new_day / N
        
    #     plt.plot(weekdays_only_patt, label='Wednesday')

    # elif new_day_wd == 4 and hol == 0:
    #     ###Thursday
    #     weekdays_only = hist[hist['weekday'] == 4]
    #     del weekdays_only['weekday']
    #     del weekdays_only['date']
    #     # print('weekday only \n', weekdays_only)
    #     weekdays_only_patt = weekdays_only.groupby(weekdays_only.index.time).mean()
    #     # print('weekday only patt mean \n', weekdays_only_patt)
    #     sum_wd_patt = weekdays_only_patt.sum()
    #     # print(sum_wd_patt)
    #     for i in range(len(weekdays_only_patt)):
    #         weekdays_only_patt.iloc[i] = weekdays_only_patt.iloc[i] / sum_wd_patt
    #     # print('weekday only patt \n', weekdays_only_patt)


    #     pat = weekdays_only_patt
    #     for i in range(len(pat)):
    #         pat.iloc[i] = pat.iloc[i] * new_day / N
        
    #     plt.plot(weekdays_only_patt, label='Thursday')

    # elif new_day_wd == 5 and hol == 0:
    #     ###Friday
    #     weekdays_only = hist[hist['weekday'] == 5]
    #     del weekdays_only['weekday']
    #     del weekdays_only['date']
    #     # print('weekday only \n', weekdays_only)
    #     weekdays_only_patt = weekdays_only.groupby(weekdays_only.index.time).mean()
    #     # print('weekday only patt mean \n', weekdays_only_patt)
    #     sum_wd_patt = weekdays_only_patt.sum()
    #     # print(sum_wd_patt)
    #     for i in range(len(weekdays_only_patt)):
    #         weekdays_only_patt.iloc[i] = weekdays_only_patt.iloc[i] / sum_wd_patt
    #     # print('weekday only patt \n', weekdays_only_patt)


    #     pat = weekdays_only_patt
    #     for i in range(len(pat)):
    #         pat.iloc[i] = pat.iloc[i] * new_day / N
        
    #     plt.plot(weekdays_only_patt, label='Friday')

    elif new_day_wd == 6 and hol == 0:
        ###saturday
        saturday_only = hist[hist['weekday'] == 5]
        del saturday_only['weekday']
        del saturday_only['date']
        # print('saturday only \n', saturday_only)
        saturday_only_patt = saturday_only.groupby(saturday_only.index.time).mean()
        # print('saturday only patt mean \n', saturday_only_patt)
        sum_sat_patt = saturday_only_patt.sum()
        # print(sum_sat_patt)
        for i in range(len(saturday_only_patt)):
            saturday_only_patt.iloc[i] = saturday_only_patt.iloc[i] / sum_sat_patt
        # print('saturday only patt \n', saturday_only_patt)

        pat = saturday_only_patt
        for i in range(len(pat)):
            pat.iloc[i] = pat.iloc[i] * new_day / N
        
        # plt.plot(saturday_only_patt, label='Saturdays')

    elif new_day_wd == 7 or hol == 1:
        ###sunday
        sunday_only = hist[hist['weekday'] == 6]
        del sunday_only['weekday']
        del sunday_only['date']
        # print('sunday only \n', sunday_only)
        sunday_only_patt = sunday_only.groupby(sunday_only.index.time).mean()
        # print('sunday only patt mean \n', sunday_only_patt)
        sum_sun_patt = sunday_only_patt.sum()
        # print(sum_sun_patt)
        for i in range(len(sunday_only_patt)):
            sunday_only_patt.iloc[i] = sunday_only_patt.iloc[i] / sum_sun_patt
        # print('saturday only patt \n', sunday_only_patt)

        pat = sunday_only_patt
        for i in range(len(pat)):
            pat.iloc[i] = pat.iloc[i] * new_day / N
        
        # plt.plot(sunday_only_patt, label='Sundays')

    else:
        print('Erro nos padrões')

    # plt.legend()
    ################
    ##Juntar timestamp

    pat_values = pat.values
    pat_values = [item for sublist in pat_values for item in sublist]
    # print(pat_values)

    # date_1 = history_sum_day.index[-1]

    pat['date'] = pat.index
    time1 = pat['date'].values
    time1 = time1[0]
    new_date = datetime.datetime.combine(date1.astype(datetime.datetime), time1)

    pat_dates = pd.date_range(
        start=new_date, periods=24/N, freq=spacing)

    # plt.figure(3)

    new_dates = [np.datetime64(x) for x in dates_h]

    # plt.plot(new_dates, values_h, 'b.-', label='Original series')
    # plt.plot(pat_dates, pat_values, 'r.-', label='Forecasted values')

    # rmse = measure_rmse(values_h[-period_estimate:], pat_values)
    # plt.title(label='Quevedo forecast // RMSE_forecast= ' + str(round(rmse, 2)))

    # plt.legend()
    # plt.show()

    # print(pat_values)

    return pat_dates, pat_values



