import sqlite3
from sqlite3 import Error

def crear_conexion():
    conn = None
    try:
        conn = sqlite3.connect('usuarios.db')
    except Error as e:
        print(e)
    return conn

def crear_tabla():
    conn = crear_conexion()
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                    );''')
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def registrar_usuario(nombre, email, password):
    conn = crear_conexion()
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO usuarios (nombre, email, password)
                     VALUES (?, ?, ?);''', (nombre, email, password))
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def obtener_usuario(email, password):
    conn = crear_conexion()
    usuario = None
    try:
        c = conn.cursor()
        c.execute('''SELECT * FROM usuarios WHERE email = ? AND password = ?;''', (email, password))
        usuario = c.fetchone()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return usuario
