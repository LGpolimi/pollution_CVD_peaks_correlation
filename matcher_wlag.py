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
            if differenza_giorni <= lag_giorni:
                matching += 1
                # Una volta trovato un match va interrotto il ciclo x il primo segnale (ho gia trovato il match)   //
                # oppure tenere anche piu di un picco ???????
                break

    kpi = (matching / (len(dsPOLL) + len(dsEMS))) * 100

    return kpi
