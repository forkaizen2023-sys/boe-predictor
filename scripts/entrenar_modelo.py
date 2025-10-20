import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib # Para guardar nuestro modelo entrenado
import os

DATASET_PATH = "data/dataset_etiquetado.csv"
MODEL_DIR = "modelos"
MODEL_PATH = os.path.join(MODEL_DIR, "modelo_impacto.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

def entrenar():
    """
    Carga los datos etiquetados, entrena un modelo de clasificacion y lo guarda.
    """
    if not os.path.exists(DATASET_PATH):
        print(f"Error: El dataset etiquetado '{DATASET_PATH}' no existe.")
        print("Ejecuta 'etiquetador_manual.py' primero.")
        return

    df = pd.read_csv(DATASET_PATH)
    # Nos aseguramos de usar solo las filas que hemos etiquetado
    df_train = df[df['impacto'].isin([0, 1])].copy()
    
    if len(df_train) < 20:
        print(f"Necesitas al menos 20 normas etiquetadas para entrenar. Tienes {len(df_train)}.")
        return

    print(f"--- Iniciando entrenamiento con {len(df_train)} normas etiquetadas ---")

    # --- Feature Engineering: Convertir texto a numeros ---
    # Usamos TfidfVectorizer, una técnica clásica y muy efectiva en NLP
    vectorizer = TfidfVectorizer(max_features=1500, stop_words=['de', 'la', 'el', 'en', 'y', 'a'])
    X = vectorizer.fit_transform(df_train['titulo'].astype(str))
    y = df_train['impacto']

    # --- Division de datos para validacion ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # --- Entrenamiento del modelo ---
    print("Entrenando el modelo RandomForest...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    # --- Evaluacion del modelo ---
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n--- Evaluacion del Modelo ---")
    print(f"Precision (Accuracy) en el set de prueba: {accuracy:.2f}")
    print("Reporte de Clasificacion:")
    print(classification_report(y_test, y_pred))

    # --- Guardado del modelo y el vectorizador ---
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"\n--- Modelo y Vectorizador guardados en la carpeta '{MODEL_DIR}' ---")

if __name__ == "__main__":
    entrenar()
