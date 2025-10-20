from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import subprocess
import sys

# --- Inicialización de la App ---
app = Flask(__name__)
CORS(app)

# --- Definición de Rutas (Endpoints) ---

@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint de salud para verificar que el servicio está activo."""
    return jsonify({"status": "ok", "message": "pong"})

@app.route("/actualizar", methods=["POST"])
def actualizar():
    """
    Endpoint para lanzar el pipeline de predicción completo.
    """
    mode = request.args.get('mode', 'sample')
    print(f"--- Peticion recibida en /actualizar (Modo: {mode}). Lanzando pipeline de IA... ---")
    
    try:
        python_executable = sys.executable
        script_path = "run_prediction_pipeline.py"
        
        comando = [python_executable, script_path]
        if mode == 'sample':
            comando.append("--muestra")

        # ---- LA CORRECCIÓN ESTÁ AQUÍ ----
        # Añadimos 'errors='replace'' para que ignore caracteres extraños en la salida.
        result = subprocess.run(
            comando,
            capture_output=True, text=True, check=True, 
            encoding='utf-8', errors='replace' 
        )
        # ---------------------------------
        
        print(f"--- Pipeline de IA (Modo: {mode}) completado con exito. ---")
        return jsonify({
            "status": "success",
            "message": f"Pipeline de prediccion (Modo: {mode}) ejecutado con exito."
        }), 200

    except subprocess.CalledProcessError as e:
        print(f"--- ERROR: El pipeline de IA (Modo: {mode}) fallo. ---")
        print("Error del script:", e.stderr)
        return jsonify({"status": "error", "message": f"Fallo la ejecucion del pipeline de IA (Modo: {mode})."}), 500
    except Exception as e:
        print(f"--- ERROR CRITICO en el endpoint /actualizar: {e} ---")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/alertas", methods=["GET"])
def get_alertas():
    """Endpoint para servir el archivo de alertas generado."""
    ALERTAS_PATH = "data/alertas.json"
    if not os.path.exists(ALERTAS_PATH):
        return jsonify([])
    try:
        with open(ALERTAS_PATH, 'r', encoding='utf-8') as f:
            data = f.read()
            if not data: return jsonify([])
            import json
            return jsonify(json.loads(data))
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error al leer o parsear alertas.json: {e}")
        return jsonify({"error": "No se pudo procesar el archivo de alertas"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)

