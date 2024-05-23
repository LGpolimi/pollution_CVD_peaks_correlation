
########################################################################################################################
########################################################################################################################

import pandas as pd
import geopandas as gpd
import numpy as np

########################################################################################################################

from peaks_calculator import *
from geomask import geomask_AREU, geomask_CAMS
from matcher_wlag import *

########################################################################################################################
########################################################################################################################

""" 
    1) Aprire il file excel compilato con tutte le specifiche ---> necessaria libreria openpyxl
    2) Salva tutte le variabili date in input nel file excel       
    3) Lettura dati geografici + funzione nome colonna        
    4) Ciclo di iterazione su ogni lag                    
"""

########################################################################################################################
########################################################################################################################


""" 1) Aprire il file excel compilato con tutte le specifiche ---> necessaria libreria openpyxl"""

percorso_excel = r"C:\Users\ASUS\Desktop\ESEMPIO.xlsx"
file_excel = pd.read_excel(percorso_excel, header=0)


########################################################################################################################


""" 2) Salva tutte le variabili date in input nel file excel"""

inquinante = file_excel['INQUINANTE'].iloc[0]
anno = file_excel['ANNO'].iloc[0]

EMS_path = file_excel['PERCORSO EMS'].iloc[0]
POLL_path = file_excel['PERCORSO POLL'].iloc[0]
KPI_path = file_excel['PERCORSO KPI'].iloc[0]
scelta_griglia = file_excel['SCELTA GRIGLIA'].iloc[0]
griglia_path = file_excel['PERCORSO GRIGLIA'].iloc[0]
popolazione_path = file_excel['PERCORSO POPOLAZIONE'].iloc[0]

perc_POLL_MIN = int(file_excel['PERCENTILE POLL MINIMO'].iloc[0])
perc_POLL_MAX = int(file_excel['PERCENTILE POLL MASSIMO'].iloc[0])
passo_POLL = float(file_excel['PASSO POLL'].iloc[0])

perc_EMS_MIN = int(file_excel['PERCENTILE EMS MINIMO'].iloc[0])
perc_EMS_MAX = int(file_excel['PERCENTILE EMS MASSIMO'].iloc[0])
passo_EMS = float(file_excel['PASSO EMS'].iloc[0])

soglia_legale = file_excel['VALORE DI SOGLIA'].iloc[0]
scelta_MAXorMEAN = file_excel['MAX or MEAN'].iloc[0]
scelta_PERCENTILEorSOGLIA = file_excel['PERC or SOGLIA'].iloc[0]


########################################################################################################################


""" 3) Lettura dati geografici + funzione nome colonna """

# Funzione per calcolare il nome della colonna dei picchi
def column_name(prefix, perc):
    return f'{prefix}_{perc}'


# Lettura dei dati geografici da shapefile

df_POLL = gpd.read_file(POLL_path)
df_AREU = gpd.read_file(EMS_path)

griglia = gpd.read_file(griglia_path)
griglia = griglia.sort_values(by = 'LMB3A_IDcu')   # serve per ordinare i dati

df_popolazione = pd.read_csv(popolazione_path)
df_popolazione = df_popolazione.sort_values(by='LMB3A_IDcu')  # serve per ordinare i dati


# Processa EMS data con geomask
elenco_df_EMS = geomask_AREU(griglia, df_AREU)


# normalizzazione su scala di 100 000 abitanti
# Itera attraverso ciascun DataFrame e normalizza la colonna 'conteggio' utilizzando la popolazione corrispondente.
for i, df in enumerate(elenco_df_EMS):
    popolazione = df_popolazione.iloc[i]['POP_2018']
    df['conteggio_normalizzato'] = df['conteggio'] / popolazione * 100000



# media mobile
for df in elenco_df_EMS:
    df.sort_values(by='DATA', inplace=True)
    df['mediamobile'] = df['conteggio_normalizzato'].rolling(window=3, min_periods=1).mean()


########################################################################################################################


""" 4) Iterazione sui lag """

for lag in range(8):

    # Creazione di un DataFrame vuoto per raccogliere tutti i KPI per il lag corrente
    df_kpi_lag = pd.DataFrame()
    # Aggiunta delle colonne per il codice della griglia
    df_kpi_lag['Codice Griglia'] = None


    # Iterazione sui percentili degli inquinanti (funzione numpy che dipende dal passo)
    for perc_POLL in np.arange(perc_POLL_MIN, perc_POLL_MAX + passo_POLL, passo_POLL):


        print(f"perc POLL =  {perc_POLL} \n ")   # per vedere a che punto siamo

        # Calcolo dei picchi atmosferici
        if scelta_PERCENTILEorSOGLIA == 'PERC':
            df_picchi_poll = peaks_perc(df_POLL, 'VALUE', perc_POLL)
        elif scelta_PERCENTILEorSOGLIA == 'SOGLIA':
            df_picchi_poll = peaks_soglialegale(df_POLL, 'VALUE', soglia_legale)
        else:
            raise ValueError('Valore non valido per scelta_PERCENTILEorSOGLIA')


        # Applica geomask e calcola i picchi divisi geograficamente
        picchi_POLL = geomask_CAMS(griglia, df_picchi_poll, scelta_MAXorMEAN)


        # Iterazione sui percentili EMS (come sopra dipende dal passo)
        for perc_EMS in np.arange(perc_EMS_MIN, perc_EMS_MAX + passo_EMS, passo_EMS):

            print(f"perc EMS =  {perc_EMS} \n ")  # per vedere a che punto siamo

            # Calcolo dei picchi EMS sulla media mobile
            picchi_EMS = [peaks_perc(df, 'mediamobile', perc_EMS) for df in elenco_df_EMS]


            # Calcola KPI e aggiunge al DataFrame per il lag corrente
            for idx, (df_poll, df_ems) in enumerate(zip(picchi_POLL, picchi_EMS)):
                kpi, match, peaks_poll, peaks_ems = comparatore(df_poll, df_ems, 'data', 'DATA', lag)
                col_name = f'LMB{scelta_griglia}_ID'
                possible_suffixes = ['cu', 'is']
                for suffix in possible_suffixes:
                    full_col_name = f'{col_name}{suffix}'
                    if full_col_name in griglia.columns:
                        codice_griglia = griglia[full_col_name].iloc[idx]
                        break


                # Nomi delle colonne basati sui percentili EMS e POLL
                kpi_col_name = column_name('KPI', f'EMS{perc_EMS}_POLL{perc_POLL}')
                picchi_poll_col_name = column_name('Picchi_POLL', perc_POLL)
                picchi_ems_col_name = column_name('Picchi_EMS', perc_EMS)
                match_col_name = column_name('Match', f'EMS{perc_EMS}_POLL{perc_POLL}')

                # Aggiunta delle informazioni aggiuntive al DataFrame
                if idx not in df_kpi_lag.index:
                    df_kpi_lag.at[idx, 'Codice Griglia'] = codice_griglia

                # Aggiunta delle colonne dei picchi e del match
                df_kpi_lag.at[idx, picchi_poll_col_name] = peaks_poll
                df_kpi_lag.at[idx, picchi_ems_col_name] = peaks_ems
                df_kpi_lag.at[idx, match_col_name] = match
                df_kpi_lag.at[idx, kpi_col_name] = kpi

    # Salvataggio del DataFrame dei KPI per il lag corrente (in automatico)
    df_kpi_lag.to_csv(f'{KPI_path}\\KPI_{inquinante}_{anno}_Griglia{scelta_griglia}_lag{lag}_{scelta_MAXorMEAN}_VARIPERCENTILI.csv', index=False)

########################################################################################################################
########################################################################################################################
