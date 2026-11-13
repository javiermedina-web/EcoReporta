from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from conexion_db import obtener_conexion
import backend_python  # al importarlo, el modelo de IA queda cargado en memoria
app = Flask(__name__)


# ------------------------- Paginas -------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Ecoreporta")
def Ecoreporta():
    return render_template("Ecoreporta.html")


@app.route("/After_reporte")
def After_reporte():
    return render_template("After_reporte.html")


@app.route("/administrador")
def administrador():
    conexion = obtener_conexion()
    if conexion is None:
        return "Error: no se pudo conectar a la base de datos.", 500

    cursor = conexion.cursor(dictionary=True)

    # Reportes con el nombre del area, la prioridad y el estado (JOINs)
    cursor.execute("""
        SELECT r.id_reporte, r.problema, r.descripcion, r.fotografia,
               DATE_FORMAT(r.fecha_reporte, '%d/%m/%Y %H:%i') AS fecha,
               r.motivo_ia,
               a.nombre_area,
               p.id_prioridad, p.nombre_prioridad,
               e.id_estado, e.nombre_estado
        FROM reportes_incidencias r
        JOIN areas_plantel a       ON r.id_area = a.id_area
        JOIN prioridades_reporte p ON r.id_prioridad = p.id_prioridad
        JOIN estados_reporte e     ON r.id_estado = e.id_estado
        ORDER BY r.id_reporte
    """)
    reportes = cursor.fetchall()

    cursor.execute("SELECT id_prioridad, nombre_prioridad "
                    "FROM prioridades_reporte ORDER BY nivel")
    prioridades = cursor.fetchall()

    cursor.execute("SELECT id_estado, nombre_estado "
                    "FROM estados_reporte ORDER BY id_estado")
    estados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("administrador.html", reportes=reportes,
                           prioridades=prioridades, estados=estados)


# ------------------------- API de la IA -------------------------

@app.route("/api/predecir", methods=["POST"])
def api_predecir():
    datos = request.get_json(force=True) or {}
    return jsonify(backend_python.predecir(datos.get("descripcion", "")))

EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
MAPA_PRIORIDADES = {"Baja": 1, "Media": 2, "Alta": 3}


@app.route("/api/reportes", methods=["POST"])
def crear_reporte():
    id_usuario = request.form.get("id_usuario", 1)
    id_area = request.form.get("id_area")
    problema = (request.form.get("problema") or "").strip()
    descripcion = (request.form.get("descripcion") or "").strip()
    foto = request.files.get("foto")

    if not id_area or not problema or not descripcion or not foto or foto.filename == "":
        return jsonify({"ok": False, "mensaje": "Todos los campos y la fotografía son obligatorios."}), 400

    ext = Path(secure_filename(foto.filename)).suffix.lower()
    if ext not in EXTENSIONES_PERMITIDAS:
        return jsonify({"ok": False, "mensaje": "Formato de imagen no válido. Usa JPG, PNG o WEBP."}), 400

    # Guardar imagen en static/UPLOADS/
    carpeta_uploads = Path(__file__).resolve().parent / "static" / "UPLOADS"
    carpeta_uploads.mkdir(parents=True, exist_ok=True)
    nombre_archivo = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    foto.save(carpeta_uploads / nombre_archivo)
    ruta_web = f"/static/UPLOADS/{nombre_archivo}"

    # Evaluar prioridad con el modelo de IA
    ia = backend_python.predecir(descripcion)
    prioridad_texto = ia["prioridad"]
    id_prioridad = MAPA_PRIORIDADES.get(prioridad_texto, 2)

    conexion = obtener_conexion()
    if conexion is None:
        return jsonify({"ok": False, "mensaje": "No se pudo conectar a la base de datos."}), 500

    cursor = conexion.cursor()
    try:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO reportes_incidencias
                (id_usuario, id_area, id_estado, id_prioridad, descripcion,
                 fecha_reporte, problema, fotografia, prioridad, motivo_ia, estado)
            VALUES (%s, %s, 1, %s, %s, %s, %s, %s, %s, %s, 'Pendiente')
        """, (
            id_usuario, id_area, id_prioridad, descripcion[:250],
            ahora, problema, ruta_web, prioridad_texto, ia["motivo"]
        ))
        id_reporte = cursor.lastrowid

        cursor.execute("""
            INSERT INTO imagenes_reporte
                (id_reporte, nombre_archivo, ruta_archivo, fecha_subida, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_reporte, nombre_archivo, ruta_web, ahora, problema))

        conexion.commit()
        return jsonify({
            "ok": True,
            "id_reporte": id_reporte,
            "prioridad": prioridad_texto,
            "confianza": ia["confianza"],
            "motivo": ia["motivo"]
        })
    except Exception as e:
        conexion.rollback()
        return jsonify({"ok": False, "mensaje": f"Error al guardar en la BD: {e}"}), 500
    finally:
        cursor.close()
        conexion.close()


# ------------------------- Acciones del panel -------------------------

@app.route("/administrador/actualizar", methods=["POST"])
def actualizar_reporte():
    datos = request.get_json(force=True)

    conexion = obtener_conexion()
    if conexion is None:
        return jsonify({"ok": False, "error": "Sin conexion a la base de datos"}), 500

    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE reportes_incidencias
        SET id_prioridad = %s, id_estado = %s
        WHERE id_reporte = %s
    """, (datos["id_prioridad"], datos["id_estado"], datos["id_reporte"]))
    conexion.commit()
    filas = cursor.rowcount
    cursor.close()
    conexion.close()

    return jsonify({"ok": True, "afectados": filas})


@app.route("/administrador/eliminar/<int:id_reporte>", methods=["POST"])
def eliminar_reporte(id_reporte):
    conexion = obtener_conexion()
    if conexion is None:
        return jsonify({"ok": False, "error": "Sin conexion a la base de datos"}), 500

    cursor = conexion.cursor()
    try:
        # historial_reparaciones NO tiene ON DELETE CASCADE: se borra antes.
        # imagenes_reporte SI tiene ON DELETE CASCADE: se borra sola.
        cursor.execute(
            "DELETE FROM historial_reparaciones WHERE id_reporte = %s", (id_reporte,))
        cursor.execute(
            "DELETE FROM reportes_incidencias WHERE id_reporte = %s", (id_reporte,))
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"ok": True})
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return jsonify({"ok": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)