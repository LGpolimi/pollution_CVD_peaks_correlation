import geopandas as gpd
import pandas as pd

########################################################################################################################


def measure_max (df, col_date, col_value):
    # Raggruppa per data e calcola il massimo per ogni data
    max_per_data = df.groupby(col_date)[col_value].max()  # max_per_data è una serie pandas

    # Converti la serie pandas in un dataframe pandas (necessario x la funzione dei picchi)

    max_x_data_df = pd.DataFrame(max_per_data).reset_index()
    max_x_data_df.columns = [col_date, 'MAX_VALUE']  # Rinomina le colonne

    return max_x_data_df


########################################################################################################################


def weighted_mean(gdf, date_column, value_column):
    """
    Calcola la media pesata dei valori per ogni data nel GeoDataFrame gdf,
    tenendo conto dell'area dei poligoni associati.

    Args:
    gdf (GeoDataFrame): GeoDataFrame contenente i dati.
    date_column (str): Nome della colonna che contiene le date.
    value_column (str): Nome della colonna che contiene i valori da mediare.

    Returns:
    DataFrame: Un DataFrame che contiene la data e la media pesata dei valori per quella data.
    """

    weighted_means = []

    # Raggruppa il GeoDataFrame per data
    grouped = gdf.groupby(date_column)

    for date, group in grouped:
        # Calcola l'area di ogni poligono
        areas = group.geometry.area

        # Calcola la somma dei valori pesati per ciascun poligono
        weighted_sum = (group[value_column] * areas).sum()

        # Calcola la somma delle aree dei poligoni
        total_area = areas.sum()

        # Calcola la media pesata dividendo la somma pesata per la somma delle aree
        if total_area == 0:
            weighted_mean = 0  # Evita divisione per zero
        else:
            weighted_mean = weighted_sum / total_area

        # Aggiungi la data e la media pesata alla lista
        weighted_means.append([date, weighted_mean])

    # Crea un DataFrame con i risultati
    result_df = pd.DataFrame(weighted_means, columns=[date_column, 'media_pesata'])

    return result_df


########################################################################################################################


def conta(df_EMS, col_data):
    # Conta le occorrenze di ciascuna data nella colonna 'data'
    conteggio_date = df_EMS[col_data].value_counts().reset_index(name='conteggio')
    conteggio_date.columns = [col_data, 'conteggio']
    return conteggio_date


########################################################################################################################


def geomask_AREU (gdf_griglia, path_AREU):

    gdf_AREU = gpd.read_file(path_AREU)

    print('\n \nIl dataframe AREU verrà suddiviso in', len(gdf_griglia), 'zone')
    print(gdf_AREU.columns)

    elenco_df = [None] * len(gdf_griglia)
    idx = 0
    df = 0

    while idx<len(gdf_griglia):
        region_geom = gdf_griglia.geometry.iloc[idx]
        region_mask = gdf_AREU.within(region_geom)
        df_region = gdf_AREU[region_mask]

    # in region_data è salvato il solo dataframe relativo alla zona della griglia.
    # da qui in poi va inserito la funzione di selezione delle misure

        elenco_df[df] = conta(df_region,'DATA')
        df += 1
        idx += 1
    return elenco_df


########################################################################################################################


def geomask_CAMS(gdf_griglia, gdf_CAMS, scelta):

    print('\n \nIl dataframe CAMS verrà suddiviso in:', len(gdf_griglia), 'zone')
    print(gdf_CAMS.columns)

    idx: int = 0
    list_gdf_CAMS = []
    list_sgn = []

    while idx < len(gdf_griglia):

        region_geom = gdf_griglia.geometry.iloc[idx]
        region_mask = gdf_CAMS.intersects(region_geom)
        gdf_x_region = gdf_CAMS[region_mask]
        list_gdf_CAMS.append(gdf_x_region)

        # in region_data è salvato il solo dataframe relativo alla zona della griglia.
        # da qui in poi va inserito la funzione di selezione delle misure

        if scelta == "MAX":
            # PER IL MASSIMO DI ogni zona
            sgn = measure_max(gdf_x_region, 'data', 'VALUE')

        elif scelta == "MEAN":
            # X LA MEDIA PESATA di ogni zona
            sgn = weighted_mean(gdf_x_region, 'data', 'VALUE')
        else:
            print("NON VA BENE!")

        # lista con tutti i dataframe
        list_sgn.append(sgn)

        idx += 1

    return list_sgn


########################################################################################################################

########################################################################################################################
