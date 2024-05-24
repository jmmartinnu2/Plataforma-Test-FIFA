import streamlit as st
from auth.database import registrar_usuario, obtener_usuario

def mostrar_registro():
    st.title("Registro de Usuario")
    nombre = st.text_input("Nombre")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    password_confirm = st.text_input("Confirmar Contraseña", type="password")
    if st.button("Registrarse"):
        if password != password_confirm:
            st.warning("Las contraseñas no coinciden")
        else:
            registrar_usuario(nombre, email, password)
            st.success("Usuario registrado exitosamente")

def mostrar_login():
    st.title("Login de Usuario")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    if st.button("Login"):
        usuario = obtener_usuario(email, password)
        if usuario:
            st.session_state.usuario = {
                "id": usuario[0],
                "nombre": usuario[1],
                "email": usuario[2]
            }
            st.success("Login exitoso")
            st.experimental_rerun()
        else:
            st.error("Email o contraseña incorrectos")
