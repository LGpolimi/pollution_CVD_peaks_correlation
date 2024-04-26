import pandas as pd
import numpy as np

#calcolo picchi, uguale per inquinamento e dati sanitari

def peaks_perc(dataframe, colonna, percentile):
    # Ottieni i dati dalla colonna specificata del df
    dati = dataframe[colonna]

    # Calcola il valore soglia utilizzando il percentile specificato
    soglia = np.percentile(dati, percentile)

    # Filtra i valori sopra la soglia
    valori_sopra_soglia = dataframe[dataframe[colonna] > soglia]

    return valori_sopra_soglia

########################################################################################################################

#implementare funzione per soglia legale, etc...
