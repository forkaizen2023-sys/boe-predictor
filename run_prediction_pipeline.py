import os
import sys
import pandas as pd
import joblib
from datetime import date
import json

# --- CAMBIO IMPORTANTE: Importamos la nueva función del nuevo archivo ---
from scripts.descargador_api import descargar_boe_api
# Ya no necesitamos el parser de XML, pero sí el clasificador
from scripts.clasificador import clasificar_sector
from scripts.alertas import generar_alertas

MODEL_PATH = "modelos/modelo_impacto.pkl"
VECTORIZER_PATH = "modelos/vectorizer.pkl"

def procesar_sumario_json(archivo_json):
    """
    Nueva función para procesar el formato JSON que nos da la API.
    Reemplaza al antiguo parser de XML.
    """
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  [ERROR] No se pudo leer o procesar el archivo JSON: {e}")
        return None
    
    normas = []
    # La estructura del JSON de la API es diferente, navegamos por ella de forma segura.
    for seccion in data.get('sumario', {}).get('diario', {}).get('seccion', []):
        # Algunos items son diccionarios, otros listas. Nos aseguramos de manejar ambos casos.
        items = seccion.get('item', [])
        if not isinstance(items, list):
            items = [items]
            
        for item in items:
            normas.append({
                'titulo': item.get('titulo'),
                'departamento': item.get('departamento'),
                # Construimos la URL completa para que sea un enlace directo
                'url_pdf': "https://www.boe.es" + item.get('urlPdf', ''),
                'tipo_norma': seccion.get('nombre')
            })
    return normas


def ejecutar_pipeline_predictivo(usar_muestra=False):
    """
    Pipeline actualizado para usar la API del BOE y procesar JSON.
    """
    print("--- Iniciando Pipeline de Prediccion (Version API v2.0) ---")

    archivo_json = None
    if usar_muestra:
        print("\n[Paso 1/5] MODO SIMULADOR ACTIVADO")
        # Para el modo muestra, ahora necesitamos un 'sample_boe.json'
        archivo_json = "data/sample_boe.json"
        if not os.path.exists(archivo_json):
            print(f"  [ERROR] Archivo de muestra '{archivo_json}' no encontrado.")
            return
        print(f"  [OK] Usando archivo de laboratorio: {archivo_json}")
    else:
        print("\n[Paso 1/5] Descargando sumario del BOE via API...")
        archivo_json, status = descargar_boe_api(date.today())
        if status not in ["DOWNLOADED", "EXISTED"]:
            print(f"  [AVISO] No se pudo descargar el sumario. Pipeline detenido. (Estado: {status})")
            return

    print("\n[Paso 2/5] Procesando normas desde JSON...")
    normas_hoy = procesar_sumario_json(archivo_json)
    if not normas_hoy:
        print("  [AVISO] No se encontraron normas validas. Pipeline finalizado.")
        return
    df_hoy = pd.DataFrame(normas_hoy)
    df_hoy['sector'] = df_hoy['titulo'].apply(clasificar_sector)
    print(f"  [OK] Se han procesado {len(df_hoy)} normas.")

    # El resto del pipeline (pasos 3, 4 y 5) no necesita cambios,
    # ya que opera sobre el DataFrame 'df_hoy', que ahora creamos a partir del JSON.
    
    print("\n[Paso 3/5] Cargando modelo de Inteligencia Artificial...")
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        print(f"  [ERROR] Modelo no encontrado. Ejecuta 'entrenar_modelo.py' primero.")
        return
    modelo = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("  [OK] Cerebro de IA cargado con exito.")

    print("\n[Paso 4/5] Realizando predicciones de impacto...")
    X_hoy = vectorizer.transform(df_hoy['titulo'].astype(str))
    predicciones = modelo.predict(X_hoy)
    df_hoy['impacto_predicho'] = predicciones
    num_alertas = df_hoy['impacto_predicho'].sum()
    print(f"  [OK] Prediccion completada. Se han detectado {num_alertas} posibles alertas.")

    print("\n[Paso 5/5] Generando archivo final de alertas...")
    generar_alertas(df_hoy)
    print("\n--- ¡Pipeline de Prediccion completado con exito! ---")

if __name__ == "__main__":
    if '--muestra' in sys.argv:
        ejecutar_pipeline_predictivo(usar_muestra=True)
    else:
        ejecutar_pipeline_predictivo(usar_muestra=False)
