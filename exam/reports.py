import os
import sqlite3
from sqlite3 import Error

# Crear el directorio data si no existe
if not os.path.exists('data'):
    os.makedirs('data')

def crear_conexion_historial():
    conn = None
    try:
        conn = sqlite3.connect('data/historial_examenes.db')
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    return conn

def crear_tabla_historial():
    conn = crear_conexion_historial()
    if conn:
        try:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS historial_examenes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            usuario_id INTEGER,
                            fecha TEXT,
                            resultado TEXT,
                            aciertos INTEGER,
                            total_preguntas INTEGER
                        );''')
            c.execute('''CREATE TABLE IF NOT EXISTS detalles_examen (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            examen_id INTEGER,
                            pregunta TEXT,
                            opciones TEXT,
                            correct_indices TEXT,
                            respuestas_usuario TEXT,
                            es_correcta INTEGER,
                            FOREIGN KEY (examen_id) REFERENCES historial_examenes (id)
                        );''')
            conn.commit()
        except Error as e:
            print(f"Error al crear la tabla: {e}")
        finally:
            if conn:
                conn.close()
    else:
        print("Error: no se pudo establecer la conexión con la base de datos.")

def guardar_resultado_examen(usuario_id, fecha, resultado, aciertos, total_preguntas, detalles):
    conn = crear_conexion_historial()
    if conn:
        try:
            c = conn.cursor()
            c.execute('''INSERT INTO historial_examenes (usuario_id, fecha, resultado, aciertos, total_preguntas)
                         VALUES (?, ?, ?, ?, ?);''', (usuario_id, fecha, resultado, aciertos, total_preguntas))
            examen_id = c.lastrowid

            for detalle in detalles:
                c.execute('''INSERT INTO detalles_examen (examen_id, pregunta, opciones, correct_indices, respuestas_usuario, es_correcta)
                             VALUES (?, ?, ?, ?, ?, ?);''', (examen_id, detalle[0], ','.join(detalle[1]), ','.join(map(str, detalle[2])), ','.join(map(str, detalle[3])), detalle[4]))
            conn.commit()
        except Error as e:
            print(f"Error al guardar el resultado del examen: {e}")
        finally:
            if conn:
                conn.close()
    else:
        print("Error: no se pudo establecer la conexión con la base de datos.")

def obtener_historial_examenes(usuario_id):
    conn = crear_conexion_historial()
    historial = []
    if conn:
        try:
            c = conn.cursor()
            c.execute('''SELECT * FROM historial_examenes WHERE usuario_id = ?;''', (usuario_id,))
            historial = c.fetchall()
        except Error as e:
            print(f"Error al obtener el historial de exámenes: {e}")
        finally:
            if conn:
                conn.close()
    else:
        print("Error: no se pudo establecer la conexión con la base de datos.")
    return historial

def obtener_detalles_examen(examen_id):
    conn = crear_conexion_historial()
    detalles = []
    if conn:
        try:
            c = conn.cursor()
            c.execute('''SELECT * FROM detalles_examen WHERE examen_id = ?;''', (examen_id,))
            detalles = c.fetchall()
        except Error as e:
            print(f"Error al obtener los detalles del examen: {e}")
        finally:
            if conn:
                conn.close()
    else:
        print("Error: no se pudo establecer la conexión con la base de datos.")
    return detalles
