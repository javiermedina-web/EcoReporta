"""
EcoReporta - Etapa 1: Entrenamiento del modelo de prioridad.
PROTOTIPO EDUCATIVO.

Qué hace:
1. Lee los ejemplos de static/datos_reportes.json
2. Convierte la descripción a números (TF-IDF) y entrena un clasificador
3. Evalúa con datos que no vio en el entrenamiento
4. Guarda el modelo en modelos/modelo_prioridad.pkl
"""

import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

# ---------- RUTAS (con pathlib da igual desde dónde se ejecute) ----------
BASE = Path(__file__).resolve().parent                      # carpeta Ecoreporta/
RUTA_DATOS = BASE / "static" / "datos_reportes.json"
RUTA_MODELO = BASE / "modelos" / "modelo_prioridad.pkl"

CLASES = ["Baja", "Media", "Alta"]


def cargar_datos():
    """Lee el JSON y devuelve (descripciones, prioridades)."""
    with open(RUTA_DATOS, "r", encoding="utf-8") as f:
        datos = json.load(f)
    textos = [d["descripcion"] for d in datos]
    etiquetas = [d["prioridad"] for d in datos]
    return textos, etiquetas


def main():
    textos, etiquetas = cargar_datos()
    print(f"Ejemplos cargados: {len(textos)}")

    # 80% para entrenar, 20% para el "examen" (datos que el modelo nunca ve)
    X_train, X_test, y_train, y_test = train_test_split(
        textos, etiquetas, test_size=0.25, random_state=42, stratify=etiquetas
    )

    # Pipeline: TF-IDF convierte texto a números; la regresión logística clasifica
    modelo = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),      # palabras solas y pares ("cables pelados")
            strip_accents="unicode"  # ignora acentos: "baño" = "bano"
        )),
        ("clf", LogisticRegression(max_iter=1000, random_state=42)),
    ])

    modelo.fit(X_train, y_train)

    predicciones = modelo.predict(X_test)
    print("\n=== Evaluación con datos de prueba (que el modelo NO vio) ===")
    print(classification_report(y_test, predicciones, labels=CLASES, zero_division=0))

    RUTA_MODELO.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, RUTA_MODELO)
    print(f"\n✅ Modelo guardado en: {RUTA_MODELO}")

    # Prueba rápida con una frase nueva
    ejemplo = ["hay cables pelados tocando el piso del salón"]
    proba = modelo.predict_proba(ejemplo)[0]
    print(f"\nPrueba rápida: '{ejemplo[0]}'")
    print("Prioridad:", modelo.predict(ejemplo)[0])
    print("Confianza:", round(float(max(proba)), 2))


if __name__ == "__main__":
    main()