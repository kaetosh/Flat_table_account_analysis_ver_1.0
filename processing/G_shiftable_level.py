import pandas as pd
from utility_functions import is_accounting_code


def shiftable_level(df):
    for j in range(3):
        list_lev = [i for i in df.columns.to_list() if 'Level' in i]
        for i in list_lev:
            # если в столбце есть и субсчет и субконто, нужно выравнивать столбцы
            if df[i].apply(is_accounting_code).nunique() == 2:
                shift_level = i  # получили столбец, в котором есть и субсчет и субконто, например Level_2
                lm = int(shift_level.split('_')[-1])  # получим его хвостик, например 2
                # получим перечень столбцов, которые бум двигать (первый - это столбец, где есть и субсчет и субконто)
                new_list_lev = list_lev[lm:]
                # сдвигаем:
                df[new_list_lev] = df.apply(
                    lambda x: pd.Series([x[i] for i in new_list_lev]) if is_accounting_code(
                        x[new_list_lev[0]]) else pd.Series([x[i] for i in list_lev[lm - 1:len(new_list_lev)]]), axis=1)
                break
    list_lev = [i for i in df.columns.to_list() if 'Level' in i]
    for n in list_lev[::-1]:
        if all(df[n].apply(is_accounting_code)):
            df['Субсчет'] = df[n].copy()
            break