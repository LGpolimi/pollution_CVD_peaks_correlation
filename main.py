import pandas as pd
import geopandas as gpd
########################################################################################################################
from peaks_calculator import *
from geomask import geomask_AREU, geomask_CAMS
from scelta_griglia import scelta_griglia_geografica
from matcher_wlag import *

########################################################################################################################

# 1. Caricamento path POLL, EMS e GRIGLIA (GEO_MASK)
# 2. Stampa columns df per leggere titoli colonne rilevanti
# 3. Ciclo programma
# 3.1 divisione df_POLL per prima area geografica
# 3.1.1 applicazione definizione e criterio di misura --> info da dare in entrata a punto #3
# 3.1.2 salvataggio in locale del segnale(?)
# 3.2 divisione df_EMS per prima area geografica
# 3.2.1 applicazione della funzione conta
# 3.1.2 salvataggio in locale del segnale(?)
# 3.3 applicazione della definizione di picco a sgn_POLL e sgn_EMS --> info su picco da dare in entrata a punto #3
# 3.3.1 salvataggio in locale delle sequenze di picco
# 3.4 matcher with lag --> info su lag da dare in entrata al punto #3
# 3.4.1 salvataggio su una list o altrove
# 3.5 iterazione per le n zone di GEO_MASK

########################################################################################################################

# 1) caricare i percorsi + scelta dell'utente per le griglie

# file AREU
EMS_path = "C:\\Users\\ASUS\\Desktop\\prova\\DATI AREU 2019\\AREU2019-CRS32632-datetime.shp"  # necessario uno shapefile

# file CAMS
CAMS_path = "C:\\Users\\ASUS\\Desktop\\Dati Inquinamento Lavorati\\dailyPM10-201819-wdate\\dailyPM10-2019_wdate.shp"  # shapefile

df_CAMS = gpd.read_file(CAMS_path)

# griglia geografica (funzione x scelta utente)
griglia, scelta_griglia = scelta_griglia_geografica()

########################################################################################################################

#picchi cams

percentile = 95

df_picchi_cams = peaks_perc(df_CAMS, 'VALUE', percentile)


########################################################################################################################

# 3) ciclo

# 3.1) poll

picchi_POLL = geomask_CAMS(griglia, df_picchi_cams)  # elenco di dataframe con il massimo giornaliero

########################################################################################################################

# 3.2) df_EMS

elenco_df_EMS = geomask_AREU(griglia,EMS_path)  # elenco di dataframe (uno ogni cella della griglia), con chiamate al giorno


########################################################################################################################

#media mobile 3 gg prima dei picchi ems


for df in elenco_df_EMS:

    df.sort_values(by = 'DATA', inplace = True)

    df['mediamobile'] = df['conteggio'].rolling(window=3, min_periods=1).mean()




########################################################################################################################

# 3.3.1) picchi EMS

# inserisce il percentile, poi esegue la funzione

while True:
    try:
        perc_ems = int(input(" \n Inserisci il valore del percentile desiderato per i dati sanitari(0-100): "))
        if 1 <= perc_ems <= 100:
            # Il valore è valido, esce dal ciclo
            break
        else:
            # Il valore non è compreso tra 1 e 100, chiedi di reinserire
            print("\n Il valore inserito non è compreso tra 1 e 100. Riprova.")
    except ValueError:
        # L'input non è un numero intero, chiedi di reinserire
        print("\n Input non valido. Inserisci un numero intero compreso tra 1 e 100.")

#picco usando il valore di media mobile

picchi_EMS = [peaks_perc(df, 'mediamobile', perc_ems) for df in elenco_df_EMS]  # salva picchi di ems


########################################################################################################################

# 4) matcher

# lag in input dall'utente
while True:
    try:
        lag = int(input("\n Inserisci un valore di lag compreso tra 0 e 7: "))  # facciamo max 7 ??
        if 0 <= lag <= 7:
            break
        else:
            print("\n il valore di lag deve essere compreso tra 0 e 7.")
    except ValueError:
        print("\n inserire un numero intero.")




# ciclo for x ogni df
df_kpi = pd.DataFrame(columns=['KPI', 'Codice Griglia', 'Match', 'Picchi cams', 'Picchi ems'])  # Creazione di un DataFrame vuoto

for idx, (df_poll, df_ems) in enumerate(zip(picchi_POLL, picchi_EMS)):
    kpi, match, peaks_poll, peaks_ems = comparatore(df_poll, df_ems, 'data', 'DATETIME', lag)


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

########################################################################################################################
# vedere poi cosa fare dei kpi!
