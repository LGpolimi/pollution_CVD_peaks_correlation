import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from geopy.distance import geodesic
import os


input_path = 'D:\\Lorenzo Documents\\Lorenzo\\Research Documents\\2023 11 -- Pollution&Health\\2404_Tesi_bachelor_POLL_CVD\\Data\\datasources\\'
output_path = 'D:\\Lorenzo Documents\\Lorenzo\\Research Documents\\2023 11 -- Pollution&Health\\2404_Tesi_bachelor_POLL_CVD\\Data\\processing\\'
if not os.path.isdir(input_path):
    os.makedirs(input_path)
if not os.path.isdir(output_path):
    os.makedirs(output_path)

def weighted_average(distances, values, max_radius=50):
    # Converti le distanze e i valori in array numpy
    distances = np.array(distances)
    values = np.array(values)

    # Filtra le stazioni entro il raggio di 50 km
    within_radius = distances <= max_radius

    # Se non ci sono stazioni entro il raggio, restituisci None o un valore di default
    if not np.any(within_radius):
        return None  # oppure un valore di default, ad esempio np.nan

    # Considera solo le stazioni entro il raggio
    filtered_distances = distances[within_radius]
    filtered_values = values[within_radius]

    # Calcola i pesi inversi alle distanze
    weights = 1 / filtered_distances

    # Calcola la media pesata
    weighted_sum = np.sum(weights * filtered_values)
    return weighted_sum / np.sum(weights)


# Coordinate delle stazioni (latitudine, longitudine) e i rispettivi dati di inquinamento
stations = pd.read_csv(input_path+'stazioni arpa/idSensori.csv')
stations = stations[stations['NomeTipoSensore'] == 'Biossido di Azoto']



stations = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(stations.lng, stations.lat),
    crs="EPSG:4326"  # Assumiamo che le coordinate delle stazioni siano in EPSG:4326
)

misure = pd.read_csv(input_path + 'stazioni arpa/ARPA_NO2_171819.csv')
misure['Data'] = pd.to_datetime(misure['Data'], format='%Y-%m-%d %H:%M:%S')


# Calcola la media giornaliera per ogni stazione
media_misure = misure.groupby(['idSensore', 'Data']).agg({'Valore': 'mean'}).reset_index()
media_misure['idSensore'] = media_misure['idSensore'].astype('int64')

media_misure['Valore'] = media_misure['Valore'].replace(-9999.00000, np.nan)

stations.rename(columns={'IdSensore': 'idSensore'}, inplace=True)

# Unisci le medie giornaliere ai dati dei sensori
stazioni = pd.merge(media_misure, stations, how='inner', on='idSensore')

# Converti in GeoDataFrame
stazioni = gpd.GeoDataFrame(stazioni, geometry='geometry')

# Definizione dei poligoni delle aree
griglia = gpd.read_file(input_path+'griglie/LMB3A.shp')

# Converti la griglia in EPSG:4326 per calcolare i centroidi correttamente
griglia = griglia.to_crs(epsg=4326)
stazioni = stazioni.dropna(subset=['Valore'])

# Ottieni un elenco di date uniche dal dataset delle misurazioni
unique_dates = stazioni['Data'].unique()

# Calcola la media pesata dell'inquinamento per ciascun giorno per ogni area della griglia
results = []
n_dates = len(unique_dates)
iti = 0

for date in unique_dates:
    stazioni_filtered = stazioni[stazioni['Data'] == date]
    iti = iti + 1
    print('Working on',date,'processing =',(iti/n_dates)*100,'%')

    for area in griglia.itertuples():  # Itera su ogni riga del GeoDataFrame delle griglie
        centroid = area.geometry.centroid  # Ottieni il centroide dell'area


        # Verifica che le coordinate del centroide siano nel range corretto
        if centroid.y < -90 or centroid.y > 90 or centroid.x < -180 or centroid.x > 180:
            print(f"Centroide non valido per l'area {area.Index}: ({centroid.y}, {centroid.x})")
            continue

        # Inizializza le liste per le distanze e i valori di inquinamento
        distances = []
        pollution_values = []

        # Itera su ogni riga del GeoDataFrame delle stazioni filtrate per data
        for station in stazioni_filtered.itertuples():
            station_coords = (station.geometry.y, station.geometry.x)  # Ottieni le coordinate della stazione corrente
            try:
                distance = geodesic((centroid.y, centroid.x), station_coords).kilometers  # Calcola la distanza
            except ValueError as e:
                print(
                    f"Errore nelle coordinate: {e}, station_coords: {station_coords}, centroid: ({centroid.y}, {centroid.x})")
                continue
            distances.append(distance)
            pollution_values.append(station.Valore)  # Aggiungi il valore di inquinamento

        # Calcola la media pesata solo se ci sono stazioni nella griglia
        if len(distances) > 0:
            weighted_avg = weighted_average(distances, pollution_values)  # Calcola la media pesata
            results.append((area.Index, area.geometry, getattr(area, 'name', 'N/A'), date, weighted_avg,
                            'NO2'))  # Aggiungi il risultato alla lista dei risultati

# Creare un DataFrame per i risultati
result_df = pd.DataFrame(results,
                         columns=['Index', 'Geometry', 'Area', 'Data', 'Weighted Average Pollution', 'Pollutant'])

result_df.to_csv(output_path+'ARPA_NO2_2023.csv')
result_df['Data'] = result_df['Data'].to_string()

# Creare un GeoDataFrame dai risultati
result_gdf = gpd.GeoDataFrame(result_df, geometry='Geometry', crs='EPSG:32632')
result_gdf.rename(columns={'Weighted Average Pollution': 'Valore'}, inplace=True)
result_gdf.drop(columns=['Index', 'Area'], inplace=True)


result_gdf.to_file(output_path+'ARPA_NO2_2023.shp')
