import pandas as pd
import os

def generar_alertas(df):
    """
    Filtra las normas predichas como de alto impacto y las guarda en un archivo JSON.
    Esta versión es robusta y compatible con todas las terminales.
    """
    # Asumimos que el DataFrame de entrada ya tiene una columna 'impacto_predicho'.
    # Nos aseguramos de manejar el caso en que la columna no exista.
    if 'impacto_predicho' not in df.columns:
        print("[ERROR] La columna 'impacto_predicho' no se encuentra en los datos.")
        return

    alertas = df[df["impacto_predicho"] == 1]
    
    output_path = "data/alertas.json"
    
    # Asegurarse de que el directorio 'data' existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Guardamos las alertas. Usamos 'force_ascii=False' para una correcta visualización de acentos.
    alertas.to_json(output_path, orient="records", indent=4, force_ascii=False)
    
    # Reemplazamos el emoji por texto simple.
    print(f"[OK] {len(alertas)} alertas/normas guardadas en {output_path}.")

