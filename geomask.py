import geopandas as gpd
import pandas as pd

########################################################################################################################

def measure_max (df, col_date, col_value):
    # Raggruppa per data e calcola il massimo per ogni data
    max_per_data = df.groupby(col_date)[col_value].max() #max_per_data è una serie pandas

    # Converti la serie pandas in un dataframe pandas (necessario x la funzione dei picchi)
    max_x_data_df = pd.DataFrame(max_per_data).reset_index()
    max_x_data_df.columns = [col_date, 'MAX_VALUE']  # Rinomina le colonne
    return max_x_data_df

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

        elenco_df[df] = conta(df_region,'DATETIME')
        df += 1
        idx += 1
    return elenco_df


########################################################################################################################


def geomask_CAMS(gdf_griglia, path_CAMS):

    gdf_CAMS = gpd.read_file(path_CAMS)

    print('\n \nIl dataframe CAMS verrà suddiviso in:', len(gdf_griglia), 'zone')
    print(gdf_CAMS.columns)

    idx: int = 0
    list_gdf_CAMS = []
    list_sgn = []

    while idx < len(gdf_griglia):

        region_geom = gdf_griglia.geometry.iloc[idx]
        region_mask = gdf_CAMS.intersects(region_geom)
        gdf_x_region = gdf_CAMS[region_mask]
        list_gdf_CAMS.append(gdf_x_region)       # si puo returnare anche questo(?); lista di df (no funzione x max)

        # in region_data è salvato il solo dataframe relativo alla zona della griglia.
        # da qui in poi va inserito la funzione di selezione delle misure

        sgn = measure_max(gdf_x_region, 'data', 'VALUE')
        list_sgn.append(sgn)

        idx += 1

    return list_sgn

########################################################################################################################
