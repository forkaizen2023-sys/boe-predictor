import pandas as pd
import os

INPUT_FILE = "data/dataset_para_etiquetar.csv"
OUTPUT_FILE = "data/dataset_etiquetado.csv"

def etiquetar_normas():
    """
    Una herramienta de CLI interactiva y robusta para etiquetar manualmente el impacto de las normas.
    Carga correctamente el progreso sin perder los nuevos datos.
    """
    if not os.path.exists(INPUT_FILE):
        print(f"Error: No se encuentra el archivo de entrada '{INPUT_FILE}'.")
        print("Ejecuta 'procesar_historicos.py' primero.")
        return

    df = pd.read_csv(INPUT_FILE)

    if os.path.exists(OUTPUT_FILE):
        print("Cargando progreso anterior...")
        df_progreso = pd.read_csv(OUTPUT_FILE)
        mapa_progreso = pd.Series(df_progreso['impacto'].values, index=df_progreso['titulo']).to_dict()
        df['impacto'] = df['titulo'].map(mapa_progreso)
    else:
        df['impacto'] = None 

    df_a_etiquetar = df[df['impacto'].isnull()].copy()
    
    if df_a_etiquetar.empty:
        print("¡Felicidades! No hay nuevas normas para etiquetar.")
        return

    print(f"--- Tienes {len(df_a_etiquetar)} nuevas normas para etiquetar ---")

    for index, row in df_a_etiquetar.iterrows():
        print("\n" + "="*80)
        original_index = df[df['titulo'] == row['titulo']].index[0]
        
        print(f"Norma {original_index + 1}/{len(df)}")
        print(f"  - Titulo: {row['titulo']}")
        print(f"  - Tipo: {row.get('tipo_norma', 'N/A')}")
        print(f"  - Sector (auto): {row['sector']}")
        
        while True:
            etiqueta = input("¿Impacto estrategico? (1=Si, 0=No, s=Saltar, q=Guardar y Salir): ")
            if etiqueta in ['1', '0']:
                df.loc[original_index, 'impacto'] = int(etiqueta)
                break
            elif etiqueta.lower() == 's':
                break
            elif etiqueta.lower() == 'q':
                # ---- LA CORRECCIÓN ESTÁ AQUÍ (Forma moderna) ----
                df['impacto'] = df['impacto'].fillna(-1)
                # --------------------------------------------------
                df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
                print(f"Progreso guardado en '{OUTPUT_FILE}'. ¡Hasta la proxima!")
                return
            else:
                print("Entrada no valida. Por favor, introduce 1, 0, s o q.")
    
    # ---- Y TAMBIÉN AQUÍ ----
    df['impacto'] = df['impacto'].fillna(-1)
    # -------------------------
    
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"¡Etiquetado completado! Archivo guardado en '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    etiquetar_normas()
