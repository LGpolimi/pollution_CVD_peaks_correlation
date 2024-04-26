
import  geopandas as gpd

#serve per far scegliere all'utente la griglia geografica desiderata

def scelta_griglia_geografica():
    # Dizionario contenente le griglie con relativi commenti

    griglie = {
        "0A": "1km hexagonal grid",
        "1A": "1km ARPA grid",
        "1B": "1.5km ARPA grid",
        "1C": "4km ARPA grid",
        "2A": "municipalities and districts",
        "2B": "municipalities",
        "2C": "municipalities for transports",
        "3A": "100k people districts",
        "3B": "EMS zones",
        "4A": "Provinces",
        "4B": "SOREU",
        "5A": "Region"
    }

    # Stampiamo l'elenco delle griglie disponibili
    print("Elenco delle griglie disponibili:")
    for codice, commento in griglie.items():
        print(f"{codice}: {commento}")

    while True:
        # Chiediamo all'utente di scegliere una griglia
        scelta = input("Inserisci il codice corrispondente alla griglia che desideri utilizzare: ").strip().upper()
        # Verifichiamo se la scelta è valida
        if scelta in griglie:
            print(f"Hai scelto la griglia con codice {scelta} - {griglie[scelta]}.")
            #scelta della griglia in base al codice, necessario che abbiano tutte lo stesso percorso
            path_griglia = f"percorso_cartella contente tutte le griglie\\LMB{scelta}.shp"
            griglia = gpd.read_file(path_griglia)
            return griglia, scelta
        else:
            print("Scelta non valida. Per favore, inserisci un codice valido.")



