"""
EcoReporta - Módulo de la IA.
Carga el modelo entrenado UNA SOLA VEZ al iniciar el servidor
y expone la funcion predecir().
"""

from pathlib import Path

import joblib

BASE = Path(__file__).resolve().parent
RUTA_MODELO = BASE / "modelos" / "modelo_prioridad.pkl"

# Orden fijo de clases: coincide con el orden en que entreno scikit-learn
CLASES = ["Baja", "Media", "Alta"]

# Al importar este archivo (app.py lo importa), el modelo queda en memoria.
# Por eso cada prediccion tarda milisegundos y no segundos.
MODELO = joblib.load(RUTA_MODELO)


def palabras_relevantes(texto, indice_clase, top_n=3):
    """Devuelve las palabras del texto que mas empujaron la decision del modelo."""
    tfidf = MODELO.named_steps["tfidf"]
    clf = MODELO.named_steps["clf"]
    X = tfidf.transform([texto])              # texto convertido a numeros
    vocabulario = tfidf.get_feature_names_out()
    pesos = clf.coef_[indice_clase]          # peso de cada palabra para esa clase
    puntuadas = sorted(
        ((pesos[i], vocabulario[i]) for i in X.indices),
        reverse=True
    )
    return [palabra for _, palabra in puntuadas[:top_n]]


def predecir(texto):
    """Analiza una descripcion y devuelve prioridad, confianza y motivo."""
    texto = (texto or "").strip()

    # Descripciones cortas no dan informacion: por seguridad, Media
    if len(texto) < 10:
        return {
            "prioridad": "Media",
            "confianza": 0.5,
            "motivo": "La descripcion es muy corta para analizarla; se asigno Media por seguridad.",
        }

    probabilidades = MODELO.predict_proba([texto])[0]
    indice = int(probabilidades.argmax())
    prioridad = CLASES[indice]
    confianza = round(float(probabilidades[indice]), 2)
    clave = ", ".join(palabras_relevantes(texto, indice))

    motivo = (
        f'El modelo detecto las palabras clave "{clave}" en la descripcion, '
        f"asociadas a reportes de prioridad {prioridad} en los datos de entrenamiento."
    )
    return {"prioridad": prioridad, "confianza": confianza, "motivo": motivo}