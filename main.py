import pandas as pd
import geopandas as gpd
########################################################################################################################
from peaks_calculator import *
from geomask import geomask_AREU, geomask_CAMS
from scelta_griglia import scelta_griglia_geografica
from matcher_wlag import  *
########################################################################################################################

#1. Caricamento path POLL, EMS e GRIGLIA (GEO_MASK)
#2. Stampa columns df per leggere titoli colonne rilevanti
#3. Ciclo programma
    #3.1 divisione df_POLL per prima area geografica
        #3.1.1 applicazione definizione e criterio di misura --> info da dare in entrata a punto #3
        #3.1.2 salvataggio in locale del segnale(?)
    #3.2 divisione df_EMS per prima area geografica
        #3.2.1 applicazione della funzione conta
        # 3.1.2 salvataggio in locale del segnale(?)
    #3.3 applicazione della definizione di picco a sgn_POLL e sgn_EMS --> info su picco da dare in entrata a punto #3
        #3.3.1 salvataggio in locale delle sequenze di picco
    #3.4 matcher with lag --> info su lag da dare in entrata al punto #3
        #3.4.1 salvataggio su una list o altrove
    #3.5 iterazione per le n zone di GEO_MASK

########################################################################################################################

# 1) caricare i percorsi + scelta dell'utente per le griglie

#file AREU
EMS_path = "percorso\\nome_file.shp"    #necessario uno shapefile

#file CAMS
CAMS_path = "percorso\\nome_file.shp"  #shapefile

#griglia geografica (funzione x scelta utente)
griglia, scelta_griglia = scelta_griglia_geografica()

########################################################################################################################

#  2) stampare colonne?? ---> le stama gia nella funzione successiva

########################################################################################################################

#3) ciclo

#3.1) poll

elenco_df_POLL = geomask_CAMS(griglia,CAMS_path)  #elenco di dataframe con il massimo giornaliero


#3.2) df_EMS

elenco_df_EMS = geomask_AREU(griglia, EMS_path)    #elenco di dataframe (uno ogni cella della griglia), con chiamate al giorno


#3.3) picchi sui df

#3.3.1) picchi EMS

#inserisce il percentile, poi esegue la funzione

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

picchi_EMS = [peaks_perc(df, 'conteggio',perc_ems) for df in elenco_df_EMS]  # salva picchi di ems


#3.3.2) picchi_CAMS

#serve x far scegliere all'utente se usare percentile o soglia; in un secondo momento implementare continuità temporale

while True:
    scelta = input(" \n Inserisci 'p' per calcolare i picchi di inquinamento atmosferico sulla base del percentile, o 's' per calcolare i picchi sulla base della soglia: ").lower()

    if scelta == 'p':
        # Operazioni per la scelta percentile
        while True:
            try:
                perc_poll = int(input(" \n Inserisci il valore del percentile desiderato per i dati atmosferici (0-100): "))
                if 1 <= perc_poll <= 100:

                    picchi_POLL = [peaks_perc(df,'MAX_VALUE', perc_poll) for df in elenco_df_POLL]  #salva picchi atmosferici

                    break
                else:
                    # se valore non è compreso tra 1 e 100
                    print("\n Il valore inserito non è compreso tra 1 e 100. Riprova.")
            except ValueError:
                # se input non è un numero intero
                print("\n Input non valido. Inserisci un numero intero compreso tra 1 e 100.")
        break

    elif scelta == 's':
        # Operazioni per la scelta soglia

        # soglia = impostare la soglia sulla base dll'inquinante

        #picchi_CAMS = [peaks_soglialegale(df,'MAX_VALUE', soglia) for df in elenco_df_POLL]

        break
    else:
        # Scelta non valida, chiedi di reinserire
        print("\nScelta non valida, ripetere")



########################################################################################################################

# 4) matcher

#lag in input dall'utente
while True:
    try:
        lag = int(input("\n Inserisci un valore di lag compreso tra 0 e 7: "))  #facciamo max 7 ??
        if 0 <= lag <= 7:
            break
        else:
            print("\n il valore di lag deve essere compreso tra 0 e 7.")
    except ValueError:
        print("\n inserire un numero intero.")


#ciclo for x ogni df
list_kpi = []   #lista di tutti i kpi con il codice corrispondente alla griglia geografica

for idx, (df_poll, df_ems) in enumerate(zip(picchi_POLL, picchi_EMS)):

    kpi = comparatore(df_poll, df_ems, 'data', 'DATA', lag)

    # Aggiungi il valore della colonna 'LMB...' ai risultati dei KPI
    kpi_wcodice = (kpi, griglia[f'LMB{scelta_griglia}_IDcu'].iloc[idx])
  
    # Aggiungi i risultati dei KPI alla lista
    list_kpi.append(kpi_wcodice)


#vedere poi cosa fare dei kpi!
########################################################################################################################
