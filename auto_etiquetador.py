import pandas as pd
import os
from tqdm import tqdm

INPUT_FILE = "data/dataset_para_etiquetar.csv"
OUTPUT_FILE = "data/dataset_etiquetado.csv"

# --- Nuestra Regla (Heurística) ---
# Si la norma pertenece a uno de estos sectores, la consideramos de alto impacto.
SECTORES_DE_IMPACTO = ["inmobiliario", "financiero", "energético"]

def auto_etiquetar():
    """
    Lee el dataset sin etiquetar y aplica una heurística simple para generar
    un dataset etiquetado automáticamente.
    """
    print(f"--- Iniciando etiquetado automatico basado en reglas ---")
    if not os.path.exists(INPUT_FILE):
        print(f"Error: No se encuentra el archivo de entrada '{INPUT_FILE}'.")
        print("Ejecuta 'generador_datos_falsos.py' primero.")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"Cargadas {len(df)} normas para auto-etiquetar.")

    # --- Aplicación de la Regla ---
    # La magia de pandas: creamos la columna 'impacto' en una sola línea.
    # .isin() comprueba si el valor de la columna 'sector' está en nuestra lista de impacto.
    # .astype(int) convierte los resultados (True/False) a 1/0.
    tqdm.pandas(desc="Aplicando reglas de impacto")
    df['impacto'] = df['sector'].isin(SECTORES_DE_IMPACTO).astype(int)

    # Contamos cuántas normas hemos clasificado como de alto impacto.
    num_impacto = df['impacto'].sum()

    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    
    print(f"\n--- ¡Exito! Etiquetado automatico completado. ---")
    print(f"  - Se han marcado {num_impacto} normas como de 'alto impacto' (1).")
    print(f"  - Dataset etiquetado guardado en '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    auto_etiquetar()