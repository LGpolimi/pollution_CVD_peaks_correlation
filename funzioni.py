import pandas as pd
import numpy as np
from datetime import datetime

#######################################################################################################
#Lista funzioni del file:
#1: filtro dati AREU (ETL)
#2: contatore EMS (extract AREU)
#3: calcolatore picchi percentile (peaks calculator)
#4: matcher (matcher, ritorna KPI)
########################################################################################################
def funzione_salute(file_path):
    try:
        df = pd.read_csv(file_path, sep='\t', encoding='latin-1')  
        
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except PermissionError:
        print(f"No permission to read the file '{file_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

    df['DATA'] = pd.to_datetime(df['DATA'], format='%d%b%Y:%H:%M:%S.%f')
    df.drop(columns=['SOREU', 'AAT', 'ZONA', 'CD_OPERATOR_SK', 'YY+MM', 'CD_EVT', 'CD_FLT', 'DT_NASCITA', 'ETA_TP',
                     'CDL_P1', 'CD_P2', 'T_OSP', '1°_IN_POSTO', 'MSI_POSTO', 'MSA_POSTO', 'DT_NUE', 'DT_ 118',
                     'FILTRO_ST', 'FILTRO_END', 'POSTO_1', 'FL_INT', 'ID_MISS_INT', 'DT_MISS_DAY', 'PUNSTA_TP',
                     'PUNSTA', 'MSB_POSTO', 'INVIO', 'CD_TOWN_ISTAT_PNT', 'OSPEDALE', 'AC_ENTE', 'CD_MISS', 'CAR',
                     'CAR_TP', 'CD_PST', 'CD_CNV', 'CONV', 'MISS_CLASS', 'CONV_TYP', 'DT_MISS', 'DT_CAR_START',
                     'DT_CAR_COME_BACK', 'DT_MISS_CLOSE', 'FL_MEDICAL', 'FL_PARAMEDIC', 'TOTKM', 'VL_ROUTE_INTERVAL',
                     'DT_ROUTE_INTERVAL_I', 'DT_STOP_INTERVAL_I', 'DT_ROUTE_INTERVAL_H', 'DT_STOP_INTERVAL_H',
                     'VL_ROUTE_INTERVAL_H', 'VL_ROUTE_INTERVAL_I', 'VL_STOP_INTERVAL_H', 'VL_STOP_INTERVAL_I'],
            inplace=True)
    df = df.loc[(df['MOTIVO'] == 'MEDICO ACUTO') & (df['MOTIVO_DTL'] == 'CARDIOCIRCOLATORIA')]

    # df['INVIO_MSA1'] = df['INVIO_MSA1'].apply(lambda x: bin(x))   come mettere valori in binaario?????
    df = df.drop_duplicates(subset=['ID_PZ', 'DATA', 'ORA'])

    return df

###############################################################################################
#conta il numero di date uguali, quindi il segnale in ingresso al peaks calculator per i dati sanitari

def conta(df, colonna):
    # Conta le occorrenze di ciascuna data nella colonna 'data'
    conteggio_date = df[colonna].value_counts().reset_index()
    conteggio_date.columns = [colonna, 'conteggio']
    return conteggio_date

################################################################################################
#calcolo picchi, uguale per inquinamento e dati sanitari

def peaks_perc(dataframe, colonna, percentile):
    # Ottieni i dati dalla colonna specificata del DataFrame
    dati = dataframe[colonna]

    # Calcola il valore soglia utilizzando il percentile specificato
    soglia = np.percentile(dati, percentile)

    # Filtra i valori sopra la soglia
    valori_sopra_soglia = dataframe[dataframe[colonna] > soglia]

    return valori_sopra_soglia

###############################################################################################
#matcher, ultima fase
# X la funzione il primo dataset deve PER FORZA essere quello dei picchi inquinanti
def comparatore(dsPOLL, dsEMS, colonnadataPOLL, colonnadataEMS, lag_giorni):
    matching = 0

    for segnale1 in dsPOLL:
        for segnale2 in dsEMS:

            data1 = dsPOLL[colonnadataPOLL]  
            data2 = dsEMS[colonnadataEMS]

            # Calcola la differenza in giorni tra le due date  --->  data limite compresa
            differenza_giorni = abs((data1 - data2).days)
            if differenza_giorni <= lag_giorni:
                matching += 1
                # Una volta trovato un match va interrotto il ciclo x il primo segnale (ho gia trovato il match)
                break

    kpi = (matching / (len(dsPOLL) + len(dsEMS))) * 100

    return kpi
