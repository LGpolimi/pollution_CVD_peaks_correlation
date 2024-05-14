# ISTRUZIONI PER L’USO

1. **Scaricare il file Excel “Specifiche di Analisi”**, specificando il percorso del file nella sezione (1) del main (`percorso_excel`).

   - *Nota:* È necessaria la libreria “openpyxl” per aprire il file.

2. **Compilare il file Excel in ogni campo** (nella riga sotto al titolo, consultare il file ESEMPIO per dubbi).
   
   - **INQUINANTE, ANNO:** Nome dell’inquinante, anno (o triennio) di riferimento.
   - **PERCORSI:** Percorsi indicati (SENZA virgolette “ ‘).
   - **PERCORSO KPI:** Cartella dove si vuole salvare i KPI da lag0 a lag7.
   - **SCELTA GRIGLIA:** Codice della griglia geografica SENZA SPAZI (es: 3A).
   - **PERCENTILI:** Valori numerici di percentili richiesti.
   - **MAX or MEAN:** Scelta tra utilizzare il valore massimo (MAX) o la media pesata (MEAN) dell’inquinante per ogni cella della griglia geografica, SENZA SPAZI.
   - **PERC or SOGLIA:** Scelta tra percentile (PERC) o soglia (SOGLIA) per i dati di inquinamento atmosferico.
   - **VALORE DI SOGLIA:** Valore numerico soglia legale (esempio per il PM2.5 = 25).
