import sys

def check_environment():
    """
    Realiza una verificación básica del entorno virtual y las dependencias clave.
    """
    print("\n" + "="*50)
    print("INICIO DE VERIFICACION BASICA DEL ENTORNO")
    print("="*50)

    # --- 1. Verificar Entorno Virtual ---
    print("\n[PASO 1] Verificando entorno virtual...")
    if sys.prefix != sys.base_prefix:
        print(f"  [OK] Entorno virtual ACTIVADO en: {sys.prefix}")
    else:
        print("  [FALLO] Entorno virtual NO esta activo. Ejecuta el script de activacion.")
        return # No tiene sentido continuar si el entorno no está activo

    # --- 2. Verificar Librerías Clave ---
    print("\n[PASO 2] Verificando librerias clave...")
    librerias_clave = ["flask", "streamlit", "pandas", "spacy", "sklearn"]
    faltantes = []
    for lib in librerias_clave:
        try:
            __import__(lib)
            print(f"  [OK] Libreria '{lib}' encontrada.")
        except ImportError:
            print(f"  [FALLO] Libreria '{lib}' NO encontrada.")
            faltantes.append(lib)

    print("\n" + "="*50)
    print("RESUMEN DE VERIFICACION")
    print("="*50)
    if not faltantes:
        print("\n¡FELICIDADES! Tu entorno basico esta correctamente configurado.")
        print("Todas las librerias clave estan instaladas y accesibles.")
    else:
        print(f"\nSe detectaron {len(faltantes)} librerias faltantes.")
        print("Ejecuta de nuevo el comando de instalacion:")
        print("python -m pip install -r requirements.txt")

if __name__ == "__main__":
    check_environment()
