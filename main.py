
########################################################################################################################

import pandas as pd
import geopandas as gpd

########################################################################################################################

from peaks_calculator import *
from geomask import geomask_AREU, geomask_CAMS
from matcher_wlag import *

########################################################################################################################
########################################################################################################################

""" 
    1) Aprire il file excel compilato con tutte le specifiche ---> necessaria libreria openpyxl
    2) Salva tutte le variabili date in input nel file excel           
    3) Salva df CAMS + Griglia + Calcolo dei picchi atmosferici        
    4) Salvataggio df EMS con Geomask + Media Mobile (3 gg) + Calcolo picchi sanitari            
    5) Matcher + Salvataggio del KPI            
"""

########################################################################################################################
########################################################################################################################


""" 1) Aprire il file excel compilato con tutte le specifiche ---> necessaria libreria openpyxl """


percorso_excel = r"C:\Users\ASUS\Desktop\ESEMPIO.xlsx"

file_excel = pd.read_excel(percorso_excel, header=0)


########################################################################################################################


""" 2) Salva tutte le variabili date in input nel file excel """


inquinante = file_excel['INQUINANTE'].iloc[0]
anno = file_excel['ANNO'].iloc[0]

EMS_path = file_excel['PERCORSO EMS'].iloc[0]
CAMS_path = file_excel['PERCORSO CAMS'].iloc[0]
KPI_path = file_excel['PERCORSO KPI'].iloc[0]

scelta_griglia = file_excel['SCELTA GRIGLIA'].iloc[0]
griglia_path = file_excel['PERCORSO GRIGLIA'].iloc[0]

perc_CAMS = file_excel['PERCENTILE CAMS'].iloc[0]
perc_EMS = file_excel['PERCENTILE EMS'].iloc[0]
soglia_legale = file_excel['VALORE DI SOGLIA'].iloc[0]

scelta_MAXorMEAN = file_excel['MAX or MEAN'].iloc[0]
scelta_PERCENTILEorSOGLIA = file_excel['PERC or SOGLIA'].iloc[0]


########################################################################################################################


""" 3) Salva df CAMS + Griglia + Calcolo dei picchi atmosferici"""


df_CAMS = gpd.read_file(CAMS_path)
griglia = gpd.read_file(griglia_path)


# Salva i picchi CAMS sul totale (NO geomask)

if scelta_PERCENTILEorSOGLIA == 'PERC':

    var = f"{scelta_PERCENTILEorSOGLIA}_{perc_CAMS}"
    df_picchi_cams = peaks_perc(df_CAMS, 'VALUE', perc_CAMS)

elif scelta_PERCENTILEorSOGLIA == 'SOGLIA':

    var = f"{scelta_PERCENTILEorSOGLIA}"
    df_picchi_cams = peaks_soglialegale(df_CAMS, 'VALUE', soglia_legale)

else:
    print('NON VA BENE')


# elenco di dataframe con il massimo/media + geomask
picchi_POLL = geomask_CAMS(griglia, df_picchi_cams, scelta_MAXorMEAN)


########################################################################################################################


""" 4) Salvataggio df EMS con Geomask + Media Mobile (3 gg) + Calcolo picchi sanitari"""


# elenco di dataframe (uno ogni cella della griglia) + conta chiamate al giorno
elenco_df_EMS = geomask_AREU(griglia, EMS_path)


# media mobile 3 gg prima dei picchi ems
for df in elenco_df_EMS:
    df.sort_values(by='DATA', inplace=True)
    df['mediamobile'] = df['conteggio'].rolling(window=3, min_periods=1).mean()


# picco usando il valore di media mobile
picchi_EMS = [peaks_perc(df, 'conteggio', perc_EMS) for df in elenco_df_EMS]


########################################################################################################################


""" 5) Matcher + Salvataggio del KPI per ogni lag """

lag = 0

# ciclo for x ogni df
while lag <= 7:

    # Creazione di un DataFrame vuoto
    df_kpi = pd.DataFrame(columns=['KPI', 'Codice Griglia', 'Match', 'Picchi cams', 'Picchi ems'])

    for idx, (df_poll, df_ems) in enumerate(zip(picchi_POLL, picchi_EMS)):
        kpi, match, peaks_poll, peaks_ems = comparatore(df_poll, df_ems, 'data', 'DATA', lag)

        # Costruzione dinamica del nome della colonna della griglia x ottenere il codice
        col_name = f'LMB{scelta_griglia}_ID'
        possible_suffixes = ['cu', 'is']
        for suffix in possible_suffixes:
            full_col_name = f'{col_name}{suffix}'
            if full_col_name in griglia.columns:
                codice_griglia = griglia[full_col_name].iloc[idx]
                break

        # Aggiunta della riga al DataFrame
        df_kpi.loc[idx] = [kpi, codice_griglia, match, peaks_poll, peaks_ems]

    # Salvataggio del KPI
    df_kpi.to_csv(f'{KPI_path}\\KPI_{inquinante}_{anno}_Griglia{scelta_griglia}_{var}_percEMS{perc_EMS}_lag{lag}_{scelta_MAXorMEAN}.csv')

    lag += 1


########################################################################################################################
