import datetime
import math
import numpy as np
import pandas as pd

# warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None


def remove_duplicates_exact(dataset):  # T1 - same timestamp, same value
    before = len(dataset)
    # print(before)
    dataset.drop_duplicates(keep='first', inplace=True)
    after = len(dataset)
    # print(after)
    # print('Tratado!', 'Removido duplicados exatos!')
    return dataset.reset_index(drop=True), before-after


def remove_duplicates_dif(dataset):  # T2 - same timestamp, different value
    counter = len(dataset)  # Tamanho da dataset
    i = 1
    indexes_remove = []
    indexes_na = []

    while i < counter:
        if dataset['date'][i] == dataset['date'][i - 1]:  # Verifica o atual sempre com o anterior
            indexes_remove.append(int(i - 1))
            indexes_na.append(int(i))
        i += 1
        counter = len(dataset)

    values = dataset['value'].values

    values[indexes_na] = np.nan  # Converte os restantes para nan

    dataset['value'] = values

    dataset = dataset.drop(index=indexes_remove)  # Remove todos os duplicados
    dataset = dataset.reset_index(drop=True)
    indexes_na = dataset['value'].index[dataset['value'].apply(np.isnan)]

    # print('Tratado!', 'Removido duplicados diferentes!')
    return dataset, indexes_remove


def remove_negatives(dataset):  # T3 - remove negatives
    values = dataset['value'].values
    date_indexes = []

    for i, value in enumerate(values):
        if value < 0:
            date_indexes.append(i)

    values[values < 0] = np.nan
    dataset['value'] = values
    # print('Tratado!', 'Removido negativos!')
    return dataset, date_indexes


def remove_pontual_zeros(dataset):  # T4 - remove pontual zeros
    indexes = []
    indexes_na = []
    values = dataset['value'].values
    for i, value in enumerate(dataset['value']):  # Procura todos os zeros e guarda o index
        if value == 0.0:
            indexes.append(i)

    for i in indexes:
        if dataset['value'][i] != dataset['value'][i - 1] \
                and dataset['value'][i] != dataset['value'][i + 1]:  # se 0 único
            indexes_na.append(i)

    values[indexes_na] = np.nan  # Vira nan
    dataset['value'] = values

    # print('Tratado!', 'Removido zeros pontuais!')
    return dataset, indexes_na


def remove_pontuals_high(dataset, win_size='', threshold=''):  # T5 - remove pontual values
    # Split into 2 arrays
    values = dataset['value'].values.copy()
    dates = dataset['date'].values.copy()

    # Create the diffs
    flow = np.diff(values)
    flow = np.insert(flow, 0, np.nan, axis=0)
    time = np.diff(dates).tolist()
    time = np.divide(time, np.power(10, 9))

    if win_size == '':
        window_size = np.median(time) * 3.5
    else:
        window_size = int(win_size)
    slopes = np.divide(flow[1:], time)  # (flow[i+1] - flow[i]) / (time[i+1] - time[i])
    slopes = np.insert(slopes, 0, 0, axis=0)

    if threshold == '':
        t = 0.3
    else:
        t = float(threshold)  # Threshold

    # ROLLING WINDOW
    size = len(dataset)
    rolling_window = []
    rolling_window_indexes = []
    RW = []
    RWi = []

    dates = dataset['date']

    # apanhar as rollings windows
    for line in range(size):
        limit_stamp = dates[line] + datetime.timedelta(seconds=window_size)
        for subline in range(line, size, 1):
            if dates[subline] <= limit_stamp:

                rolling_window.append(slopes[subline])  # Valores para RW
                rolling_window_indexes.append(subline)

            else:

                RW.append(rolling_window)
                if line != size:
                    rolling_window = []

                RWi.append(rolling_window_indexes)
                if line != size:
                    rolling_window_indexes = []

                break
    else:

        RW.append(rolling_window)
        RWi.append(rolling_window_indexes)

    peaks = []
    for index, rollWin in enumerate(RW):
        if rollWin[0] > t:
            bottom = np.min(rollWin)

            if bottom < -t:
                bottomIndex = int(np.argmin(rollWin))

                for peak in range(0, bottomIndex, 1):
                    peaks.append(RWi[index][peak])

    dataset['value'][peaks] = np.nan

    # print('Tratado!', 'Removido picos pontuais!')
    return dataset, peaks, flow, slopes


def remove_pontuals_low(dataset, win_size='', threshold=0.3):  # T6 - remove pontual values
    try:

        values = dataset['value'].values.copy()
        dates = dataset['date'].values.copy()

        flow = np.diff(values)
        flow = np.insert(flow, 0, np.nan, axis=0)
        time = np.diff(dates).tolist()
        time = np.divide(time, np.power(10, 9))

        if win_size == '':
            window_size = np.median(time) * 3.5
        else:
            window_size = int(win_size)

        slopes = np.divide(flow[1:], time)  # (flow[i+1] - flow[i]) / (time[i+1] - time[i])
        slopes = np.insert(slopes, 0, 0, axis=0)

        size = len(dataset)
        rolling_window = []
        rolling_window_indexes = []
        RW = []
        RWi = []

        dates = [i.to_pydatetime() for i in dataset['date']]
        dates = np.array(dates)

        # create the rollings windows
        for line in range(size):
            limit_stamp = dates[line] + datetime.timedelta(seconds=window_size)
            for subline in range(line, size, 1):
                if dates[subline] <= limit_stamp:

                    rolling_window.append(slopes[subline])  # Values of the slopes
                    rolling_window_indexes.append(subline)  # Indexes of the respective values

                else:

                    RW.append(rolling_window)
                    if line != size:  # To prevent clearing the last rolling window
                        rolling_window = []

                    RWi.append(rolling_window_indexes)
                    if line != size:
                        rolling_window_indexes = []
                    break
        else:
            # To get the last rolling window since it breaks before append
            RW.append(rolling_window)
            RWi.append(rolling_window_indexes)

        t = float(threshold)  # Threshold
        peaks = []

        for index, rollWin in enumerate(RW):
            if rollWin[0] < -t:  # If the first value is greater of threshold
                bottom = np.max(rollWin)  # Finds the minimum of the peak

                if bottom > t:  # If less than the negative threshold
                    bottomIndex = int(np.argmax(rollWin))  # Find it's index

                    for peak in range(0, bottomIndex,
                                      1):  # Appends all points between the first index of the rolling window until the bottomIndex
                        peaks.append(RWi[index][peak])

        dataset['value'][peaks] = np.nan

        # print('Tratado!', 'Removido picos baixos pontuais!')
        return dataset, peaks, flow, slopes


    except ZeroDivisionError:
        print('Erro!', 'Os dados contêm valores a zeros! Por favor remova-os primeiro.')


def remove_flat_lines(dataset, win_size='', threshold=0.85):  # T7 - remove flat lines
    # Split into 2 arrays
    values = dataset['value'].values
    dates = [i.to_pydatetime() for i in dataset['date']]
    dates = np.array(dates)

    # Create the diffs
    flow = np.diff(values)  # a[t+1] - a[t]
    t = float(threshold)
    string = ""
    for i, value in enumerate(np.abs(flow)):
        if value > t:
            string += "0"
        #Bruno 07/08
        elif math.isnan(value):
            string+= "0"
        ####
        else:
            string += "1"
    # ROLLING WINDOW
    size = len(string)
    rolling_window = []
    rolling_window_indexes = []
    RW = []
    RWi = []
    # print(string)
    d = dataset['date'].values.copy()

    time = np.diff(d).tolist()
    time = np.divide(time, np.power(10, 9))

    if win_size == '':
        window_size = np.median(time) * 3.5
    else:
        window_size = int(win_size)

    # apanhar as rollings windows
    for line in range(size):
        limit_stamp = dates[line] + datetime.timedelta(seconds=window_size)
        for subline in range(line, size, 1):
            if dates[subline] <= limit_stamp:

                rolling_window.append(string[subline])  # Valores para RW
                rolling_window_indexes.append(subline)

            else:

                RW.append(rolling_window)
                if line != size:
                    rolling_window = []

                RWi.append(rolling_window_indexes)
                if line != size:
                    rolling_window_indexes = []

                break
    else:
        RW.append(rolling_window)
        RWi.append(rolling_window_indexes)

    flines = []
    beginFlatLine = True
    FLIndexes = []

    for index, rollWin in enumerate(RW):
        if "0" not in rollWin and beginFlatLine:
            FLIndexes.append(RWi[index][0])
            beginFlatLine = not beginFlatLine

        if "0" in rollWin and not beginFlatLine:
            beginFlatLine = not beginFlatLine

    endFlatLine = False
    for i in FLIndexes:
        while not endFlatLine:
            flines.append(i)
            try:
                if string[i + 1] != '1':
                    endFlatLine = True
            except:
                flines.append(i + 1)
                break
            i += 1
        flines.append(i)
        endFlatLine = False
    else:
        flines.append(i)

    values[flines] = np.nan
    dataset['value'] = values
    # print(flines)
    # print('Tratado!', 'Removido patamares!')
    return dataset, flines


def new_remove_flat_lines(dataset, win_size=0, threshold=float(0)):
    dates = dataset['date']
    values = dataset['value']
    # print(win_size, threshold)
    flat_points = []
    for row, date in enumerate(dates):
        if math.isnan(values[row]):
            continue
        rolling_window = []
        flag = 0
        end = date + datetime.timedelta(seconds=win_size)

        upper_limit = values[row] + threshold
        lower_limit = values[row] - threshold

        counter = row
        while end > dates[counter]:
            rolling_window.append(counter)
            if counter < len(dates) - 1:
                counter += 1
            else:
                break

        for row_RW in rolling_window:
            if values[row_RW] > upper_limit or values[row_RW] < lower_limit or math.isnan(values[row]):
                flag = 1
                break

        flat_line_window = []

        while flag == 0:
            if values[row] > upper_limit or values[row] < lower_limit or math.isnan(values[row]):
                flag = 1
            else:
                flat_line_window.append(row)

            if row < len(dates) - 1:
                row += 1
            else:
                break

        if len(flat_line_window) > 1:
            flat_points.append(flat_line_window)
    flat_list = [item for sublist in flat_points for item in sublist]
    flat_list = list(set(flat_list))
    values[flat_list] = np.nan
    dataset['value'] = values
    # print('Tratado!', 'Removido patameres!')
    return dataset, flat_list


def remove_all(dataset, PH_WS, PH_T, PL_WS, PL_T, FL_WS, FL_T):
    try:
        remove_duplicates_exact(dataset)
        remove_duplicates_dif(dataset)
        remove_pontual_zeros(dataset)
        remove_pontuals_high(dataset, win_size=PH_WS, threshold=PH_T)
        remove_pontuals_low(dataset, win_size=PL_WS, threshold=PL_T)
        remove_flat_lines(dataset, win_size=FL_WS, threshold=FL_T)

        # print('Tratado!', 'Removido todas as anomalias!')
    except:
        print('Erro!', 'Ocorreu um erro, por favor tente remover as anomalias individualmente')


def spacing(dataset):
    sum = 0
    time_spacing = np.zeros(len(dataset) - 1)
    dates = dataset['date'].values
    for line in range(1, len(dataset), 1):
        time_spacing[line - 1] = float((dates[line] - dates[line - 1]) / np.power(10, 9))  # Conversao ns para s
        sum += float((dates[line] - dates[line - 1]) / np.power(10, 9))

    time_spacing = pd.DataFrame(time_spacing)
    # print('Espacamento', time_spacing.describe().to_string())


def statistics(dataset):
    print(dataset['value'].describe().to_string())
