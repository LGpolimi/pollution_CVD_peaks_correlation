import pandas as pd
from datetime import datetime

#matcher, ultima fase
# X la funzione il primo dataset deve PER FORZA essere quello dei picchi inquinanti

def comparatore(dsPOLL, dsEMS, colonnadataPOLL, colonnadataEMS, lag_giorni):
    matching = 0

    for index1, row1 in dsPOLL.iterrows():
        for index2, row2 in dsEMS.iterrows():

            data1 = datetime.strptime(row1[colonnadataPOLL], '%Y-%m-%d')
            data2 = datetime.strptime(row2[colonnadataEMS], '%Y-%m-%d')

            # Calcola la differenza in giorni tra le due date  --->  data limite compresa
            differenza_giorni = abs((data1 - data2).days)
            if differenza_giorni == lag_giorni:
                matching += 1
                # Puoi registrare il match trovato, ad esempio, aggiungendolo a una lista
                # matches.append((index1, index2))  # Dove index1 e index2 sono gli indici dei picchi di POLL e EMS
                break

    if len(dsPOLL) == 0:
        kpi = 0
    else:
        kpi = (matching / (len(dsPOLL))) * 100

    ###########################################################################à

    return kpi, matching, len(dsPOLL), len(dsEMS)

