import requests
from datetime import date
import os
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
if not log.handlers:
    os.makedirs("logs", exist_ok=True)
    handler = logging.FileHandler("logs/descargas.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.addHandler(logging.StreamHandler())

def descargar_boe(dia=None):
    dia_obj = date.fromisoformat(dia) if dia else date.today()
    dia_str_archivo = dia_obj.strftime("%Y-%m-%d")
    dia_str_url = dia_obj.strftime("%Y%m%d")

    url = f"https://www.boe.es/diario_boe/xml.php?id=BOE-S-{dia_str_url}"
    carpeta = "data/raw_boe"
    archivo = os.path.join(carpeta, f"boe_{dia_str_archivo}.xml")

    if os.path.exists(archivo):
        log.info(f"Archivo '{archivo}' ya existe. No se necesita descarga.")
        return archivo, "EXISTED"

    log.info(f"Intentando descargar BOE del {dia_str_archivo}...")
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()

        os.makedirs(carpeta, exist_ok=True)
        with open(archivo, "wb") as f:
            f.write(r.content)
        
        log.info(f"[OK] BOE del {dia_str_archivo} descargado en {archivo}") # Emoji eliminado
        return archivo, "DOWNLOADED"
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            log.warning(f"No se encontro BOE para la fecha {dia_str_archivo}.")
        else:
            log.error(f"[ERROR] HTTP {e.response.status_code} al descargar BOE.")
        return None, "HTTP_ERROR"
    except requests.exceptions.RequestException as e:
        log.error(f"[ERROR] de red al descargar BOE: {e}")
        return None, "NETWORK_ERROR"

if __name__ == "__main__":
    descargar_boe()

