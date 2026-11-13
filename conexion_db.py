"""
EcoReporta - Conexion a la base de datos MySQL/MariaDB.
Requiere: pip install mysql-connector-python
"""

import mysql.connector
from mysql.connector import Error

# ---------- CONFIGURACION (cambia estos datos por los tuyos) ----------
DB_CONFIG = {
    "host": "localhost",       # o "127.0.0.1"
    "user": "root",            # tu usuario de MySQL
    "password": "",            # TU CONTRASEÑA AQUI
    "database": "eco_reporta",
    "port": 3306,
}


def obtener_conexion():
    """Abre y devuelve una conexion a la base de datos."""
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None
