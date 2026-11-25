from flask import Flask, render_template, request, jsonify
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

    # 1. Tabla de reportes con area, prioridad y estado (JOINs)
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

    # 2. Estadisticas para el DASHBOARD ---------------------------

    # Total de reportes
    cursor.execute("SELECT COUNT(*) AS total FROM reportes_incidencias")
    stats = cursor.fetchone()  # {"total": N}

    # Conteo por estado (LEFT JOIN para incluir estados sin reportes)
    cursor.execute("""
        SELECT e.nombre_estado, COUNT(r.id_reporte) AS total
        FROM estados_reporte e
        LEFT JOIN reportes_incidencias r ON r.id_estado = e.id_estado
        GROUP BY e.id_estado, e.nombre_estado
        ORDER BY e.id_estado
    """)
    por_estado = cursor.fetchall()

    # Conteo por prioridad
    cursor.execute("""
        SELECT p.nombre_prioridad, COUNT(r.id_reporte) AS total
        FROM prioridades_reporte p
        LEFT JOIN reportes_incidencias r ON r.id_prioridad = p.id_prioridad
        GROUP BY p.id_prioridad, p.nombre_prioridad
        ORDER BY p.nivel
    """)
    por_prioridad = cursor.fetchall()

    # Conteo por area
    cursor.execute("""
        SELECT a.nombre_area, COUNT(r.id_reporte) AS total
        FROM areas_plantel a
        LEFT JOIN reportes_incidencias r ON r.id_area = a.id_area
        GROUP BY a.id_area, a.nombre_area
        ORDER BY total DESC
    """)
    por_area = cursor.fetchall()

    # 3. Listas para los select del editor ------------------------
    cursor.execute("SELECT id_prioridad, nombre_prioridad "
                    "FROM prioridades_reporte ORDER BY nivel")
    prioridades = cursor.fetchall()

    cursor.execute("SELECT id_estado, nombre_estado "
                    "FROM estados_reporte ORDER BY id_estado")
    estados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("administrador.html", reportes=reportes,
                           stats=stats, por_estado=por_estado,
                           por_prioridad=por_prioridad, por_area=por_area,
                           prioridades=prioridades, estados=estados)


# ------------------------- API de la IA -------------------------

@app.route("/api/predecir", methods=["POST"])
def api_predecir():
    datos = request.get_json(force=True) or {}
    return jsonify(backend_python.predecir(datos.get("descripcion", "")))


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