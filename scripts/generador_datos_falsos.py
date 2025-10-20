import pandas as pd
import random
import os
from clasificador import clasificar_sector # Reutilizamos nuestro clasificador
from tqdm import tqdm

# --- "Ingredientes" para generar títulos de normas realistas ---
ACCIONES = ["Real Decreto sobre", "Resolución para la", "Anuncio de licitación de", "Concesión de subvenciones para", "Modificación de la ley de", "Orden ministerial sobre"]
SECTORES_TEMAS = {
    "inmobiliario": ["vivienda protegida", "rehabilitación de edificios", "mercado del alquiler", "urbanismo sostenible"],
    "financiero": ["ayudas directas a pymes", "impuestos sobre el patrimonio", "regulación bancaria", "fondos de inversión"],
    "energético": ["energía eólica marina", "el autoconsumo eléctrico", "combustibles sintéticos", "la red de distribución eléctrica"],
    "otros": ["la pesca de bajura", "la sanidad animal", "el patrimonio cultural", "la seguridad vial"]
}
DEPARTAMENTOS = ["MINISTERIO DE ECONOMÍA", "MINISTERIO DE HACIENDA", "MINISTERIO DE TRANSPORTES", "MINISTERIO PARA LA TRANSICIÓN ECOLÓGICA", "MINISTERIO DE CULTURA"]
TIPOS_NORMA = ["Disposiciones generales", "Anuncios", "Autoridades y personal"]

def generar_titulo_aleatorio():
    """Genera un título de norma plausible de forma aleatoria."""
    accion = random.choice(ACCIONES)
    sector = random.choice(list(SECTORES_TEMAS.keys()))
    tema = random.choice(SECTORES_TEMAS[sector])
    return f"{accion} {tema}."

def generar_dataset_falso(num_filas=200):
    """
    Crea un DataFrame de pandas con datos sintéticos que imitan al BOE.
    """
    print(f"--- Generando un dataset sintetico de {num_filas} normas ---")
    datos = []
    for _ in tqdm(range(num_filas), desc="Generando datos"):
        datos.append({
            "titulo": generar_titulo_aleatorio(),
            "departamento": random.choice(DEPARTAMENTOS),
            "tipo_norma": random.choice(TIPOS_NORMA),
            "url_pdf": "/boe_sintetico.pdf"
        })
    
    df = pd.DataFrame(datos)
    
    print("\n--- Aplicando clasificador de sectores a los datos generados ---")
    tqdm.pandas(desc="Clasificando sectores")
    df['sector'] = df['titulo'].progress_apply(clasificar_sector)
    
    output_filename = "data/dataset_para_etiquetar.csv"
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"\n--- ¡Exito! Dataset sintetico guardado en '{output_filename}' ---")

if __name__ == "__main__":
    generar_dataset_falso(num_filas=200)

