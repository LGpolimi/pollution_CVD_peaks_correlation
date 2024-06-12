from datetime import datetime

########################################################################################################################

# X la funzione il primo dataset deve PER FORZA essere quello dei picchi inquinanti

def comparatore(dsPOLL, dsEMS, colonnadataPOLL, colonnadataEMS, lag_giorni):
    matching = 0

    # Creare un set per tenere traccia delle date in dsEMS che hanno già un match
    matched_dates_in_dsEMS = set()

    for index1, row1 in dsPOLL.iterrows():
        data1 = datetime.strptime(row1[colonnadataPOLL], '%Y-%m-%d')

        for index2, row2 in dsEMS.iterrows():
            # Verificare se la data in dsEMS è già stata associata
            if index2 not in matched_dates_in_dsEMS:
                data2 = datetime.strptime(row2[colonnadataEMS], '%Y-%m-%d')

                differenza_giorni = abs((data1 - data2).days)
                if differenza_giorni == lag_giorni:
                    matching += 1
                    # Contrassegnare la data in dsEMS come già associata
                    matched_dates_in_dsEMS.add(index2)
                    # Esci dal loop per evitare confronti multipli per la stessa data in dsPOLL
                    break  # Esci dal loop interno

    if len(dsPOLL) == 0:
        kpi = 0
    else:
        kpi = (matching / len(dsPOLL)) * 100

    return kpi, matching, len(dsPOLL), len(dsEMS)

########################################################################################################################

