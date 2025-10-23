import requests
from datetime import date
import os
import logging
import json

# --- Configuración del Logging ---
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
if not log.handlers:
    os.makedirs("logs", exist_ok=True)
    handler = logging.FileHandler("logs/descargas_api.log", encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.addHandler(logging.StreamHandler())

# --- Constante para la URL base de la API ---
API_BASE_URL = "https://www.boe.es/datosabiertos/api/boe/sumario/"

def descargar_boe_api(fecha: date):
    """
    Descarga el sumario del BOE para una fecha específica usando la API oficial.
    Guarda el resultado en un archivo JSON.
    """
    fecha_str_url = fecha.strftime("%Y%m%d")
    fecha_str_archivo = fecha.strftime("%Y-%m-%d")
    
    url = f"{API_BASE_URL}{fecha_str_url}"
    
    # El archivo de salida ahora será un .json
    carpeta = "data/raw_boe_json"
    archivo = os.path.join(carpeta, f"boe_{fecha_str_archivo}.json")

    # Verificamos si ya existe para no descargarlo de nuevo
    if os.path.exists(archivo):
        log.info(f"Archivo '{archivo}' ya existe. No se necesita descarga.")
        return archivo, "EXISTED"

    log.info(f"Intentando descargar sumario del {fecha_str_archivo} desde la API...")
    try:
        # La API requiere que especifiquemos que aceptamos JSON
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers, timeout=30)
        
        # La API puede devolver 200 OK pero con un mensaje de error dentro del JSON.
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                log.warning(f"La API devolvió un error para la fecha {fecha_str_archivo}: {data['error']['mensaje']}")
                return None, "API_ERROR"
        else:
             # Si el código no es 200, lanzamos una excepción para que la capture el bloque except.
            response.raise_for_status()

        os.makedirs(carpeta, exist_ok=True)
        with open(archivo, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        log.info(f"[OK] Sumario del {fecha_str_archivo} descargado en {archivo}")
        return archivo, "DOWNLOADED"
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            log.warning(f"No se encontró sumario para la fecha {fecha_str_archivo}. Posiblemente no hubo publicación.")
        else:
            log.error(f"[ERROR] HTTP {e.response.status_code} al descargar desde la API.")
        return None, "HTTP_ERROR"
    except requests.exceptions.RequestException as e:
        log.error(f"[ERROR] de red al descargar desde la API: {e}")
        return None, "NETWORK_ERROR"

if __name__ == "__main__":
    descargar_boe_api(date.today())
