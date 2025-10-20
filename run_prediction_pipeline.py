import os
import sys
import pandas as pd
import joblib
from scripts.actualizador_diario import descargar_boe
from scripts.parser_normas import parsear_boe
from scripts.clasificador import clasificar_sector
from scripts.alertas import generar_alertas

MODEL_PATH = "modelos/modelo_impacto.pkl"
VECTORIZER_PATH = "modelos/vectorizer.pkl"

def ejecutar_pipeline_predictivo(usar_muestra=False):
    """
    Orquesta el pipeline completo de predicción.
    Incluye un modo de muestra para usar datos de laboratorio.
    """
    print("--- Iniciando Pipeline de Prediccion ---")

    archivo_xml = None
    if usar_muestra:
        print("\n[Paso 1/5] MODO SIMULADOR ACTIVADO")
        archivo_xml = "data/sample_boe.xml"
        if not os.path.exists(archivo_xml):
            print(f"  [ERROR] Archivo de muestra '{archivo_xml}' no encontrado.")
            return
        print(f"  [OK] Usando archivo de laboratorio: {archivo_xml}")
    else:
        print("\n[Paso 1/5] Descargando BOE del dia...")
        archivo, status = descargar_boe()
        if status not in ["DOWNLOADED", "EXISTED"]:
            print(f"  [AVISO] No se pudo descargar el BOE. Pipeline detenido. (Estado: {status})")
            return
        archivo_xml = archivo

    print("\n[Paso 2/5] Procesando nuevas normas...")
    normas_hoy = parsear_boe(archivo_xml)
    if not normas_hoy:
        print("  [AVISO] No se encontraron normas validas. Pipeline finalizado.")
        return
    df_hoy = pd.DataFrame(normas_hoy)
    df_hoy['sector'] = df_hoy['titulo'].apply(clasificar_sector)
    print(f"  [OK] Se han procesado {len(df_hoy)} normas.")

    print("\n[Paso 3/5] Cargando modelo de Inteligencia Artificial...")
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        print(f"  [ERROR] Modelo no encontrado en la carpeta '{os.path.dirname(MODEL_PATH)}'.")
        print("  Asegurate de haber ejecutado 'scripts/entrenar_modelo.py' primero.")
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
    print("--- El archivo 'data/alertas.json' ha sido actualizado con las predicciones de la IA. ---")
    print("--- Ya puedes lanzar la API y el Dashboard para ver los resultados. ---")

if __name__ == "__main__":
    if '--muestra' in sys.argv:
        ejecutar_pipeline_predictivo(usar_muestra=True)
    else:
        ejecutar_pipeline_predictivo(usar_muestra=False)
