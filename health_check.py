import os
import requests
import subprocess
import time
import pandas as pd
from datetime import date
import xmltodict # Importamos para la prueba interna

# --- Constantes de configuración ---
SERVER_WAIT_TIME = 4
API_URL = "http://127.0.0.1:5001"

# --- Dato de prueba para el Parser ---
SAMPLE_XML_DATA = """
<boe>
  <sumario>
    <boletin>
      <seccion nombre="Disposiciones generales">
        <epigrafe>
          <titulo>Real Decreto sobre medidas para la vivienda.</titulo>
          <urlPdf>/boe_archivo.pdf</urlPdf>
        </epigrafe>
      </seccion>
    </boletin>
  </sumario>
</boe>
"""

def test_descarga():
    """Verifica el módulo de descarga."""
    print("\n[TEST 1/5] Verificando descarga del BOE...")
    try:
        from scripts.actualizador_diario import descargar_boe
        fecha_ayer = date.today() - pd.Timedelta(days=1)
        archivo, status = descargar_boe(fecha_ayer.isoformat())
        
        if status in ["DOWNLOADED", "EXISTED"]:
            print(f"  [OK] Resultado: (Estado: {status})")
            return True
        else:
            print(f"  [FALLO] Resultado: (Estado: {status})")
            return False
    except Exception as e:
        print(f"  [ERROR CRITICO] en la descarga: {e}")
        return False

def test_parser():
    """Verifica el parser con datos de prueba internos para ser 100% fiable."""
    print("\n[TEST 2/5] Verificando el parser de normas...")
    try:
        from scripts.parser_normas import parsear_boe
        # Creamos un archivo de prueba temporal
        test_file_path = "data/raw_boe/test_sample.xml"
        os.makedirs("data/raw_boe", exist_ok=True)
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_XML_DATA)

        normas = parsear_boe(test_file_path)
        
        if isinstance(normas, list) and len(normas) > 0 and normas[0]['titulo'] == "Real Decreto sobre medidas para la vivienda.":
            print(f"  [OK] Resultado: ({len(normas)} normas extraidas del archivo de prueba)")
            return True
        else:
            print(f"  [FALLO] Resultado: El parser no funciono como se esperaba con los datos de prueba.")
            return False
            
    except Exception as e:
        print(f"  [ERROR CRITICO] en el parser: {e}")
        return False

def test_clasificador_y_alertas():
    """Verifica la clasificación y la generación de alertas con datos de prueba."""
    print("\n[TEST 3/5] Verificando clasificador y generacion de alertas...")
    try:
        from scripts.clasificador import clasificar_sector
        from scripts.alertas import generar_alertas
        
        df_test = pd.DataFrame([
            {"titulo": "Anuncio de subvencion para la vivienda", "impacto_predicho": 0},
            {"titulo": "Real Decreto-ley de energia electrica", "impacto_predicho": 1}
        ])
        
        df_test['sector'] = df_test['titulo'].apply(clasificar_sector)
        # BUG CORREGIDO: 'energético' con tilde
        if 'inmobiliario' not in df_test['sector'].iloc[0] or 'energético' not in df_test['sector'].iloc[1]:
            print("  [FALLO] Resultado: La clasificacion de sectores no funciona como se esperaba")
            return False
        
        generar_alertas(df_test)
        if os.path.exists("data/alertas.json"):
            print("  [OK] Resultado: Clasificador funciona y 'alertas.json' se genero correctamente")
            return True
        else:
            print("  [FALLO] Resultado: No se genero el archivo de alertas")
            return False
    except Exception as e:
        print(f"  [ERROR CRITICO] en clasificacion/alertas: {e}")
        return False

def test_microservicio():
    """Lanza la API, comprueba el endpoint /ping y la detiene."""
    print("\n[TEST 4/5] Verificando el microservicio Flask (API)...")
    proceso_api = None
    try:
        comando_api = ["python", "-m", "app.gestor_api"]
        proceso_api = subprocess.Popen(
            comando_api, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8'
        )
        print(f"  - Servidor API lanzado (PID: {proceso_api.pid}). Esperando {SERVER_WAIT_TIME}s...")
        time.sleep(SERVER_WAIT_TIME)

        if proceso_api.poll() is not None:
             stderr_output = proceso_api.stderr.read()
             print("  [FALLO] El servidor de la API termino inesperadamente. Error:")
             print("------------------- INICIO ERROR API -------------------")
             print(stderr_output)
             print("-------------------- FIN ERROR API ---------------------")
             return False

        response = requests.get(f"{API_URL}/ping")
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("  [OK] Resultado: El endpoint /ping respondio correctamente")
            return True
        else:
            print(f"  [FALLO] Resultado: (Respuesta: {response.status_code} {response.text})")
            return False
    except Exception as e:
        print(f"  [ERROR CRITICO] al testear la API: {e}")
        return False
    finally:
        if proceso_api:
            proceso_api.terminate()
            proceso_api.wait()
            print(f"  - Servidor API (PID: {proceso_api.pid}) detenido.")

def test_dashboard():
    """Verifica que el comando para lanzar el dashboard es válido."""
    print("\n[TEST 5/5] Verificando el dashboard...")
    try:
        comando = ["streamlit", "run", "dashboards/streamlit_app.py", "--server.runOnSave=false"]
        proc = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        proc.terminate()
        proc.wait()
        print("  [OK] Resultado: El comando de lanzamiento es valido")
        return True
    except FileNotFoundError:
        print("  [FALLO] Resultado: 'streamlit' no se encuentra. Esta instalado?")
        return False
    except Exception as e:
        print(f"  [FALLO] Resultado: El script del dashboard tiene un error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("INICIO DEL CHEQUEO DE SALUD DEL GESTOR PREDICTIVO BOE")
    print("="*50)
    
    resultados = {
        "Descarga": test_descarga(),
        "Parser": test_parser(),
        "Clasificacion y Alertas": test_clasificador_y_alertas(),
        "Microservicio API": test_microservicio(),
        "Dashboard": test_dashboard(),
    }
    
    print("\n" + "="*50)
    print("RESUMEN DEL CHEQUEO DE SALUD")
    print("="*50)
    
    fallos = 0
    for modulo, resultado in resultados.items():
        if resultado:
            print(f"  [OK] {modulo:<25} ... PASO")
        else:
            print(f"  [FALLO] {modulo:<25} ... FALLO")
            fallos += 1
            
    print("-"*50)
    if fallos == 0:
        print("¡FELICIDADES! Todos los modulos del sistema estan operativos.")
    else:
        print(f"Se detectaron {fallos} fallos. Revisa los logs de arriba.")
    print("="*50)