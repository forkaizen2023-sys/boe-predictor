from datetime import date, timedelta
# Asegúrate de importar la función desde el archivo correcto en la misma carpeta 'scripts'
from actualizador_diario import descargar_boe
import time
import os

def descargar_rango_fechas(fecha_inicio, fecha_fin):
    """
    Descarga los boletines del BOE para un rango de fechas específico,
    limpiando previamente los datos antiguos para asegurar un dataset limpio.
    """
    print(f"--- Iniciando expedicion arqueologica de datos del BOE ---")
    print(f"--- Rango de busqueda: de {fecha_inicio} a {fecha_fin} ---")
    
    raw_dir = "data/raw_boe"
    if os.path.exists(raw_dir):
        print("Limpiando yacimiento de datos antiguos...")
        # Eliminamos todos los archivos dentro de la carpeta, pero no la carpeta en sí
        for f in os.listdir(raw_dir):
            os.remove(os.path.join(raw_dir, f))
    else:
        os.makedirs(raw_dir)

    fecha_actual = fecha_inicio
    dias_totales = (fecha_fin - fecha_inicio).days + 1
    dias_procesados = 0

    while fecha_actual <= fecha_fin:
        dias_procesados += 1
        print(f"Excavando fecha: {fecha_actual.isoformat()} ({dias_procesados}/{dias_totales})")
        descargar_boe(fecha_actual.isoformat())
        time.sleep(1) # Pausa de 1 segundo para no saturar el servidor del BOE
        fecha_actual += timedelta(days=1)
        
    print("\n--- Expedicion completada ---")

if __name__ == "__main__":
    # Viajamos 180 días (6 meses) al pasado y descargamos un bloque de 30 días.
    # Esto aumenta masivamente la probabilidad de encontrar datos no corruptos.
    hoy = date.today()
    fecha_fin_descarga = hoy - timedelta(days=180)
    fecha_inicio_descarga = fecha_fin_descarga - timedelta(days=30)
    
    descargar_rango_fechas(fecha_inicio_descarga, fecha_fin_descarga)
