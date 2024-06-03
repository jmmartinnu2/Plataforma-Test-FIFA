import random
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
from examen_fifa import preguntas_por_categoria  # Asegúrate de que este archivo está en el mismo directorio
from auth.database import crear_tabla
from exam.config import ExamConfig
from exam.exam_manager import ExamManager
from exam.reports import crear_tabla_historial, guardar_resultado_examen, obtener_historial_examenes, obtener_detalles_examen
import time
import os

# Contraseña correcta definida
CONTRASEÑA_CORRECTA = "030616"

# Variable para mantener el estado de la sesión
if 'sesion_iniciada' not in st.session_state:
    st.session_state['sesion_iniciada'] = False
    
    
    
    

# Función para mostrar la pantalla de inicio de sesión
def mostrar_login():
    st.title("Inicio de Sesión")
    contraseña = st.text_input("Introduce la contraseña", type="password")
    if st.button("Iniciar sesión"):
        if contraseña == CONTRASEÑA_CORRECTA:
            st.session_state['sesion_iniciada'] = True
            st.experimental_rerun()
        else:
            st.error("Contraseña incorrecta. Acceso denegado.")

# Función para inicializar o resetear la sesión
def iniciar_sesion():
    return {
        'preguntas': [],
        'realizado_test': False,
    }

# Crear el directorio data si no existe
if not os.path.exists('data'):
    os.makedirs('data')

# Establecer la configuración de la página
st.set_page_config(page_title="Examen FIFA", layout="centered")

# Crear la tabla de usuarios y la tabla de historial de exámenes
crear_tabla()
crear_tabla_historial()

# Función para cargar archivos markdown
def cargar_markdown(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: El archivo {file_path} no se encontró."

# Función para calcular el resultado
def calcular_resultado(preguntas, respuestas_usuario):
    respuestas_correctas = 0
    resultados = []
    feedback = []
    for i, pregunta in enumerate(preguntas):
        try:
            correct_indices = [pregunta['opciones'].index(resp) for resp in pregunta['respuestas_correctas']]
        except ValueError as e:
            st.error(f"Error en la pregunta {i+1}: {str(e)}")
            continue
        es_correcta = respuestas_usuario[i] == [1 if idx in correct_indices else 0 for idx in range(len(pregunta['opciones']))]
        if es_correcta:
            respuestas_correctas += 1
            feedback.append((pregunta['pregunta'], "Respuesta correcta"))
        else:
            feedback.append((pregunta['pregunta'], "Respuesta incorrecta", pregunta['respuestas_correctas']))
        resultados.append((pregunta['pregunta'], pregunta['opciones'], correct_indices, respuestas_usuario[i], es_correcta))
    return respuestas_correctas, resultados, feedback

# Función para seleccionar preguntas basadas en temas
def seleccionar_preguntas_por_temas(preguntas_por_categoria, temas_seleccionados, num_preguntas, historial_preguntas):
    todas_las_preguntas = []
    if not temas_seleccionados:  # Si no se seleccionan temas, usar todas las preguntas
        for categoria in preguntas_por_categoria.values():
            todas_las_preguntas.extend(categoria)
    else:
        for tema in temas_seleccionados:
            todas_las_preguntas.extend(preguntas_por_categoria[tema])
    
    # Excluir preguntas que han sido usadas en los últimos dos exámenes
    preguntas_disponibles = [p for p in todas_las_preguntas if p['pregunta'] not in historial_preguntas]

    # Verificar si hay suficientes preguntas disponibles
    if len(preguntas_disponibles) < num_preguntas:
        st.warning(f"No hay suficientes preguntas disponibles para los temas seleccionados. Máximo disponible: {len(preguntas_disponibles)}")
        return []

    # Seleccionar preguntas sin reemplazo
    preguntas_seleccionadas = random.sample(preguntas_disponibles, num_preguntas)
    
    return preguntas_seleccionadas

# Función para actualizar el historial de preguntas
def actualizar_historial_preguntas(nuevas_preguntas, num_preguntas):
    st.session_state.historial_preguntas.extend(nuevas_preguntas)
    # Mantener solo las preguntas de los últimos dos exámenes
    if len(st.session_state.historial_preguntas) > 2 * num_preguntas:
        st.session_state.historial_preguntas = st.session_state.historial_preguntas[-2 * num_preguntas:]

# Función para actualizar el temporizador
def actualizar_temporizador():
    now = datetime.now()
    remaining_time = st.session_state.end_time - now

    if remaining_time.total_seconds() > 0:
        minutes, seconds = divmod(remaining_time.total_seconds(), 60)
        timer_placeholder.info(f"Tiempo restante: {int(minutes):02}:{int(seconds):02}")
        if minutes < 5:  # Recordatorio si quedan menos de 5 minutos
            st.warning("Quedan menos de 5 minutos.")
        return True
    else:
        timer_placeholder.warning("Tiempo terminado")
        return False

# Historial de preguntas usadas en los últimos dos exámenes
if 'historial_preguntas' not in st.session_state:
    st.session_state.historial_preguntas = []

# Mostrar pantalla de inicio de sesión si no se ha iniciado sesión
if not st.session_state['sesion_iniciada']:
    mostrar_login()
else:
    # Opciones de navegación después de iniciar sesión
    opcion = st.sidebar.selectbox("Selecciona una opción", ["Configurar Examen", "Historial de Exámenes", "Resultados Detallados"])

    if opcion == "Configurar Examen":
        # Configuración del examen
        st.title("Configuración del Examen")
        num_preguntas = st.number_input("Número de Preguntas", min_value=1, max_value=100, value=20)
        tiempo_limite = st.number_input("Tiempo Límite (minutos)", min_value=1, max_value=180, value=60)
        orden_aleatorio = st.checkbox("Orden Aleatorio de Preguntas", value=True)

        temas = list(preguntas_por_categoria.keys())
        temas_seleccionados = st.multiselect("Selecciona los temas", temas, default=temas)

        config = ExamConfig(num_preguntas=num_preguntas, tiempo_limite=tiempo_limite, orden_aleatorio=orden_aleatorio)
        exam_manager = ExamManager(config)

        if st.button("Iniciar Examen"):
            st.session_state.exam_manager = exam_manager
            st.session_state.start_time = datetime.now()  # Start timer
            st.session_state.end_time = st.session_state.start_time + exam_manager.get_tiempo_limite()
            st.session_state.temas_seleccionados = temas_seleccionados
            st.session_state.respuestas_usuario = []
            st.session_state.mostrar_resultados = False
            st.session_state.ver_correccion = False
            st.session_state.feedback = []
            st.session_state.preguntas = seleccionar_preguntas_por_temas(preguntas_por_categoria, temas_seleccionados, num_preguntas, st.session_state.historial_preguntas)
            if st.session_state.preguntas:  # Verifica si se seleccionaron preguntas
                actualizar_historial_preguntas([p['pregunta'] for p in st.session_state.preguntas], num_preguntas)
                st.experimental_rerun()

    if 'exam_manager' in st.session_state and st.session_state.exam_manager:
        exam_manager = st.session_state.exam_manager
        preguntas = st.session_state.preguntas

        # Crear un espacio vacío para el temporizador
        timer_placeholder = st.sidebar.empty()

        # Llamada inicial para mostrar el temporizador
        if not actualizar_temporizador():
            st.stop()

        # Crear un formulario para el examen
        if not st.session_state.mostrar_resultados and not st.session_state.ver_correccion:
            with st.form("examen"):
                respuestas_usuario = []
                submit_attempted = False
                for i, pregunta in enumerate(preguntas):
                    st.markdown(f"### Pregunta {i+1}")
                    st.markdown(f"**{pregunta['pregunta']}**")
                    selected_options = [st.checkbox(opt, key=f"q{i}_opt{j}") for j, opt in enumerate(pregunta['opciones'])]
                    respuestas_usuario.append(selected_options)
                    if submit_attempted and not any(selected_options):
                        st.warning("Debe seleccionar al menos una opción para esta pregunta.", icon="⚠️")
                    st.markdown("---")  # Añadir una línea divisoria entre preguntas

                submitted = st.form_submit_button("Enviar Examen")
                if submitted:
                    submit_attempted = True

            # Validar las respuestas del usuario
            if submitted:
                sin_responder = [i + 1 for i, options in enumerate(respuestas_usuario) if not any(options)]
                if sin_responder:
                    st.warning("Debe seleccionar al menos una opción para cada pregunta.", icon="⚠️")
                else:
                    st.session_state.respuestas_usuario = respuestas_usuario
                    respuestas_usuario = [[1 if opt else 0 for opt in q] for q in respuestas_usuario]
                    respuestas_correctas, resultados, feedback = calcular_resultado(preguntas, respuestas_usuario)
                    st.session_state.respuestas_correctas = respuestas_correctas
                    st.session_state.resultados = resultados
                    st.session_state.feedback = feedback
                    st.session_state.mostrar_resultados = True
                    guardar_resultado_examen(
                        0,  # Asignar un id por defecto ya que no hay usuario
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'APTO' if respuestas_correctas >= 15 else 'NO APTO',
                        respuestas_correctas,
                        len(preguntas),
                        resultados
                    )
                    st.experimental_rerun()

        elif st.session_state.mostrar_resultados:
            # Mostrar resultado general
            st.markdown(f"### Resultado final: {'APTO' if st.session_state.respuestas_correctas >= 15 else 'NO APTO'} - Aciertos: {st.session_state.respuestas_correctas}/20")
            if st.button("Ver corrección"):
                st.session_state.ver_correccion = True
                st.experimental_rerun()

        # Mostrar corrección detallada
        if st.session_state.ver_correccion:
            st.markdown("## Resultados del Examen")
            for idx, (pregunta, opciones, correct_indices, respuestas_usuario, es_correcta) in enumerate(st.session_state.resultados):
                st.markdown(f"### Pregunta {idx+1}: {pregunta}")
                for i, opcion in enumerate(opciones):
                    if i in correct_indices:
                        st.markdown(f"- **{opcion}** :green_heart:")
                    elif respuestas_usuario[i] == 1:
                        st.markdown(f"- ~~{opcion}~~ :red_circle:")
                    else:
                        st.markdown(f"- {opcion}")
                st.markdown("---")

            st.markdown(f"### Resultado final: {'APTO' if st.session_state.respuestas_correctas >= 15 else 'NO APTO'} - Aciertos: {st.session_state.respuestas_correctas}/20")
            if st.button("Generar nuevo Examen"):
                config = st.session_state.exam_manager.config
                exam_manager = ExamManager(config)
                st.session_state.exam_manager = exam_manager
                st.session_state.start_time = datetime.now()  # Reset timer
                st.session_state.end_time = st.session_state.start_time + exam_manager.get_tiempo_limite()
                st.session_state.respuestas_usuario = []
                st.session_state.mostrar_resultados = False
                st.session_state.ver_correccion = False
                st.experimental_rerun()

        # Actualizar el temporizador cada segundo
        if not st.session_state.mostrar_resultados and not st.session_state.ver_correccion:
            while True:
                if not actualizar_temporizador():
                    break
                time.sleep(1)
                st.experimental_rerun()

    if opcion == "Historial de Exámenes":
        st.title("Historial de Exámenes")
        historial = obtener_historial_examenes(0)  # Usar 0 como id por defecto para el historial
        if historial:
            df_historial = pd.DataFrame(historial, columns=["ID", "Usuario ID", "Fecha", "Resultado", "Aciertos", "Total Preguntas"])
            st.dataframe(df_historial)
            st.download_button(
                "Descargar como CSV",
                data=df_historial.to_csv(index=False).encode('utf-8'),
                file_name="historial_examenes.csv",
                mime="text/csv"
            )

            examen_id = st.selectbox("Selecciona un examen para ver los detalles", df_historial["ID"].tolist())
            if st.button("Ver Detalles"):
                st.session_state.examen_id = examen_id
                st.experimental_rerun()

    if opcion == "Resultados Detallados" or ('examen_id' in st.session_state and st.session_state.examen_id):
        st.title("Resultados Detallados")
        if 'examen_id' in st.session_state:
            detalles = obtener_detalles_examen(st.session_state.examen_id)
            if detalles:
                for idx, detalle in enumerate(detalles):
                    pregunta, opciones, correct_indices, respuestas_usuario, es_correcta = detalle[2], detalle[3].split(','), list(map(int, detalle[4].split(','))), list(map(int, detalle[5].split(','))), detalle[6]
                    st.markdown(f"### Pregunta {idx+1}: {pregunta}")
                    for i, opcion in enumerate(opciones):
                        if i in correct_indices:
                            st.markdown(f"- **{opcion}** :green_heart:")
                        elif i < len(respuestas_usuario) and respuestas_usuario[i] == 1:
                            st.markdown(f"- ~~{opcion}~~ :red_circle:")
                        else:
                            st.markdown(f"- {opcion}")
                    st.markdown("---")
            else:
                st.info("No hay resultados detallados disponibles.")
        else:
            st.info("Selecciona un examen del historial para ver los detalles.")
