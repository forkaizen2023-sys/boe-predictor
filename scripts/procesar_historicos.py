import os
import pandas as pd
from parser_normas import parsear_boe
from clasificador import clasificar_sector
from tqdm import tqdm
import sys

def consolidar_historicos(usar_muestra=False, output_filename="data/dataset_para_etiquetar.csv"):
    """
    Lee los archivos XML, los procesa y los consolida en un CSV.
    Incluye un modo de muestra para usar datos de laboratorio.
    """
    lista_completa_normas = []
    
    if usar_muestra:
        print("--- Ejecutando en MODO MUESTRA ---")
        sample_file = "data/sample_boe.xml"
        if not os.path.exists(sample_file):
            print(f"Error: El archivo de muestra '{sample_file}' no existe.")
            return
        normas = parsear_boe(sample_file)
        if normas:
            lista_completa_normas.extend(normas)
    else:
        # Lógica original
        raw_dir = "data/raw_boe"
        if not os.path.exists(raw_dir) or not os.listdir(raw_dir):
            print(f"Error: La carpeta '{raw_dir}' no existe o está vacía. Ejecuta 'descargar_historicos.py' primero.")
            return

        xml_files = [f for f in os.listdir(raw_dir) if f.endswith(".xml")]
        archivos_fallidos = []
        
        print(f"--- Procesando {len(xml_files)} archivos XML ---")
        for filename in tqdm(xml_files, desc="Procesando archivos"):
            ruta_completa = os.path.join(raw_dir, filename)
            normas = parsear_boe(ruta_completa)
            if normas:
                lista_completa_normas.extend(normas)
            else:
                archivos_fallidos.append(filename)

        print(f"\nResumen: {len(xml_files) - len(archivos_fallidos)} archivos procesados con exito, {len(archivos_fallidos)} descartados.\n")

    if not lista_completa_normas:
        print("Proceso detenido: no se pudieron extraer normas validas.")
        return

    df = pd.DataFrame(lista_completa_normas)
    
    print("--- Clasificando sectores ---")
    tqdm.pandas(desc="Clasificando sectores")
    df['sector'] = df['titulo'].progress_apply(clasificar_sector)
    
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"\n--- Proceso completado. Dataset con {len(df)} normas guardado en '{output_filename}' ---")

if __name__ == "__main__":
    # La línea de abajo es la que hemos corregido. Hemos eliminado el '1' final.
    if '--muestra' in sys.argv:
        consolidar_historicos(usar_muestra=True)
    else:
        consolidar_historicos(usar_muestra=False)
