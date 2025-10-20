import xmltodict
import os

def parsear_boe(xml_path):
    """
    Parsea un archivo XML del BOE y extrae las disposiciones de forma segura.
    """
    if not os.path.exists(xml_path):
        print(f"❌ Error: El archivo {xml_path} no existe.")
        return []
        
    with open(xml_path, "rb") as f:
        try:
            data = xmltodict.parse(f)
        except Exception as e:
            print(f"❌ Error al parsear el archivo XML {xml_path}: {e}")
            return []
    
    procesadas = []
    sumario = data.get("boe", {}).get("sumario", {})
    boletines = sumario.get("boletin", [])
    if not isinstance(boletines, list):
        boletines = [boletines]

    for boletin in boletines:
        secciones = boletin.get("seccion", [])
        if not isinstance(secciones, list):
            secciones = [secciones]

        for seccion in secciones:
            disposiciones = seccion.get("epigrafe", [])
            if not isinstance(disposiciones, list):
                disposiciones = [disposiciones]

            for dispo in disposiciones:
                procesadas.append({
                    "titulo": dispo.get("titulo"),
                    "url_pdf": dispo.get("urlPdf"),
                    "departamento": dispo.get("departamento", "No especificado"),
                    "fecha_publicacion": os.path.basename(xml_path).replace('boe_', '').replace('.xml', '').replace('_', '-'),
                    "tipo_norma": seccion.get("@nombre", "No especificado")
                })
    return procesadas
