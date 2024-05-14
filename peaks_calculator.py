import numpy as np
import pandas as pd

########################################################################################################################

# calcolo picchi percentile, uguale per inquinamento e dati sanitari

def peaks_perc(dataframe, colonna, percentile):

    # Verifica se la colonna esiste nel dataframe e se non è vuota    UTILE PER GRIGLIE PICCOLE!!
    if colonna not in dataframe.columns or dataframe[colonna].empty:
        # Se la colonna non esiste o è vuota, restituisci una colonna vuota
        return pd.DataFrame(columns=dataframe.columns)

    # Ottieni i dati dalla colonna specificata del df
    dati = dataframe[colonna]

    # Calcola il valore soglia utilizzando il percentile specificato
    soglia = np.percentile(dati, percentile)

    # Filtra i valori sopra la soglia
    valori_sopra_soglia = dataframe[dataframe[colonna] > soglia]

    return valori_sopra_soglia

########################################################################################################################


# picco con soglia legale

def peaks_soglialegale(dataframe, colonna, valore_soglia):

    # Verifica se la colonna esiste nel dataframe e se non è vuota      UTILE PER GRIGLIE PICCOLE!!
    if colonna not in dataframe.columns or dataframe[colonna].empty:
        # Se la colonna non esiste o è vuota, restituisci una colonna vuota
        return pd.DataFrame(columns=dataframe.columns)

    valori_sopra_soglia = dataframe[dataframe[colonna] > valore_soglia]

    return  valori_sopra_soglia

########################################################################################################################

# CONTINUITA' dei picchi ??????

