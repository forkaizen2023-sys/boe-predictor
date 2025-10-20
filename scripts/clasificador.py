import re

# Versión mejorada: Las expresiones regulares ahora aceptan vocales con o sin tilde.
# Por ejemplo, [ií] significa "una 'i' o una 'í'".
SECTORES_KEYWORDS = {
    "inmobiliario": r"\b(vivienda|inmueble|alquiler|hipotecario|urbanismo)\b",
    "financiero": r"\b(subvenci[oó]n|ayuda|impuesto|financiero|banco|bancario|econ[oó]mico)\b",
    "energético": r"\b(energ[ií]a|el[eé]ctrico|renovable|combustible|el[eé]ctrica)\b",
}

def clasificar_sector(texto):
    """
    Clasifica el texto de una norma en un sector predefinido usando palabras clave.
    Esta versión es robusta y no es sensible a las tildes.
    """
    if not texto or not isinstance(texto, str):
        return "desconocido"
    
    texto_lower = texto.lower()
    
    for sector, pattern in SECTORES_KEYWORDS.items():
        if re.search(pattern, texto_lower):
            return sector
            
    return "otros"
