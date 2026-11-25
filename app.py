from flask import Flask, render_template, request, jsonify
from conexion_db import obtener_conexion
import backend_python
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Carpeta donde se guardan las fotos
UPLOAD_FOLDER = os.path.join("static", "UPLOADS")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB máximo

# Mapeo de nombre de prioridad → id de la tabla
PRIORIDAD_A_ID = {
    "Baja": 1,
    "Media": 2,
    "Alta": 3
}


# ------------------------- Páginas -------------------------

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

    # Tabla de reportes
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
        ORDER BY r.id_reporte DESC
    """)
    reportes = cursor.fetchall()

    # Estadísticas
    cursor.execute("SELECT COUNT(*) AS total FROM reportes_incidencias")
    stats = cursor.fetchone()

    cursor.execute("""
        SELECT e.nombre_estado, COUNT(r.id_reporte) AS total
        FROM estados_reporte e
        LEFT JOIN reportes_incidencias r ON r.id_estado = e.id_estado
        GROUP BY e.id_estado, e.nombre_estado
        ORDER BY e.id_estado
    """)
    por_estado = cursor.fetchall()

    cursor.execute("""
        SELECT p.nombre_prioridad, COUNT(r.id_reporte) AS total
        FROM prioridades_reporte p
        LEFT JOIN reportes_incidencias r ON r.id_prioridad = p.id_prioridad
        GROUP BY p.id_prioridad, p.nombre_prioridad
        ORDER BY p.nivel
    """)
    por_prioridad = cursor.fetchall()

    cursor.execute("""
        SELECT a.nombre_area, COUNT(r.id_reporte) AS total
        FROM areas_plantel a
        LEFT JOIN reportes_incidencias r ON r.id_area = a.id_area
        GROUP BY a.id_area, a.nombre_area
        ORDER BY total DESC
    """)
    por_area = cursor.fetchall()

    cursor.execute("SELECT id_prioridad, nombre_prioridad FROM prioridades_reporte ORDER BY nivel")
    prioridades = cursor.fetchall()

    cursor.execute("SELECT id_estado, nombre_estado FROM estados_reporte ORDER BY id_estado")
    estados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("administrador.html",
                           reportes=reportes,
                           stats=stats,
                           por_estado=por_estado,
                           por_prioridad=por_prioridad,
                           por_area=por_area,
                           prioridades=prioridades,
                           estados=estados)


# ------------------------- API de la IA (pruebas) -------------------------

@app.route("/api/predecir", methods=["POST"])
def api_predecir():
    datos = request.get_json(force=True) or {}
    return jsonify(backend_python.predecir(datos.get("descripcion", "")))


# ------------------------- API PRINCIPAL: crear reporte -------------------------

@app.route("/api/reportes", methods=["POST"])
def api_reportes():
    try:
        # 1. Datos del formulario
        id_usuario = request.form.get("id_usuario", 1)
        id_area = request.form.get("id_area")
        problema = request.form.get("problema", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not id_area or not problema or not descripcion:
            return jsonify({"ok": False, "mensaje": "Faltan datos obligatorios."}), 400

        # 2. Llamar a la IA
        resultado_ia = backend_python.predecir(descripcion)
        prioridad_nombre = resultado_ia["prioridad"]          # "Baja", "Media" o "Alta"
        id_prioridad = PRIORIDAD_A_ID.get(prioridad_nombre, 2)
        confianza = resultado_ia["confianza"]
        motivo = resultado_ia["motivo"]

        # 3. Guardar la foto (si viene)
        nombre_foto = None
        foto = request.files.get("foto")
        if foto and foto.filename:
            extension = foto.filename.rsplit(".", 1)[-1].lower()
            if extension not in ("jpg", "jpeg", "png", "webp"):
                return jsonify({"ok": False, "mensaje": "Solo se permiten imágenes JPG, PNG o WEBP."}), 400

            nombre_seguro = secure_filename(foto.filename)
            nombre_foto = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
            ruta_completa = os.path.join(app.config["UPLOAD_FOLDER"], nombre_foto)
            foto.save(ruta_completa)

        # 4. Guardar en la base de datos
        conexion = obtener_conexion()
        if conexion is None:
            return jsonify({"ok": False, "mensaje": "No se pudo conectar a la base de datos."}), 500

        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO reportes_incidencias
                (id_usuario, id_area, id_estado, id_prioridad,
                 descripcion, fecha_reporte, problema, fotografia,
                 prioridad, motivo_ia, estado)
            VALUES
                (%s, %s, 1, %s, %s, NOW(), %s, %s, %s, %s, 'Pendiente')
        """, (
            id_usuario,
            id_area,
            id_prioridad,
            descripcion,
            problema,
            nombre_foto,
            prioridad_nombre,
            motivo
        ))
        conexion.commit()
        id_reporte = cursor.lastrowid
        cursor.close()
        conexion.close()

        # 5. Respuesta que espera el JavaScript del frontend
        return jsonify({
            "ok": True,
            "id_reporte": id_reporte,
            "prioridad": prioridad_nombre,
            "confianza": confianza,
            "motivo": motivo
        })

    except Exception as e:
        print("Error en /api/reportes:", e)
        return jsonify({"ok": False, "mensaje": str(e)}), 500


# ------------------------- Acciones del panel de administrador -------------------------

@app.route("/administrador/actualizar", methods=["POST"])
def actualizar_reporte():
    datos = request.get_json(force=True)

    conexion = obtener_conexion()
    if conexion is None:
        return jsonify({"ok": False, "error": "Sin conexión a la base de datos"}), 500

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
        return jsonify({"ok": False, "error": "Sin conexión a la base de datos"}), 500

    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM historial_reparaciones WHERE id_reporte = %s", (id_reporte,))
        cursor.execute("DELETE FROM reportes_incidencias WHERE id_reporte = %s", (id_reporte,))
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