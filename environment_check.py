def generar_informe_html(resultados):
    """Genera un informe HTML simple con los resultados de las pruebas."""
    html = "<html><head><title>Informe de Chequeo de Entorno</title></head>"
    html += "<body style='font-family: sans-serif;'>"
    html += "<h1>📊 Informe de Chequeo de Entorno</h1>"
    for modulo, resultado in resultados.items():
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        color = "green" if resultado else "red"
        html += f"<p><b>{modulo}:</b> <span style='color:{color};'>{estado}</span></p>"
    html += "</body></html>"

    with open("informe_entorno.html", "w") as f:
        f.write(html)
    print("\n📄 Informe HTML generado en 'informe_entorno.html'")

# Y al final del bloque __main__:
if __name__ == "__main__":
    # ... (código existente)
    generar_informe_html(resultados)

**2. Endpoint `/test` en Flask:**
#Esta es una práctica estándar en microservicios para la monitorización. Convertir nuestro script en una función que pueda ser llamada desde la API es muy sencillo.

**Añade este endpoint a `app/gestor_api.py`:**
```python
# En gestor_api.py, necesitarías importar las funciones de environment_check
# (esto requiere estructurar el código para evitar dependencias circulares,
# pero conceptualmente sería así)

@app.route("/test-environment", methods=["GET"])
def test_environment():
    # Aquí llamarías a las funciones de chequeo
    # y construirías una respuesta JSON.
    resultados = {
        "entorno_virtual": True, # Placeholder, aquí iría la lógica real
        "dependencias": True,
        # ... etc
    }
    status_code = 200 if all(resultados.values()) else 500
    return jsonify(resultados), status_code
