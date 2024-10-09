import random
from datetime import datetime
import streamlit as st
import pandas as pd
import os

# Asegúrate de que estos archivos existen y tienen las variables correctas
from examen_fifa import preguntas_por_categoria  
from exam.config import ExamConfig
from exam.exam_manager import ExamManager
from exam.reports import guardar_resultado_examen, obtener_historial_examenes, obtener_detalles_examen
from examen_prueba import preguntas_prueba

# Contraseña correcta definida
CONTRASEÑA_CORRECTA = "091086"

# Inicializar el estado de la sesión
if 'sesion_iniciada' not in st.session_state:
    st.session_state['sesion_iniciada'] = False

if 'modo_prueba' not in st.session_state:
    st.session_state['modo_prueba'] = False

if 'historial_preguntas' not in st.session_state:
    st.session_state['historial_preguntas'] = []

# Crear el directorio data si no existe
if not os.path.exists('data'):
    os.makedirs('data')

# Establecer la configuración de la página
st.set_page_config(page_title="Examen FIFA", layout="centered")

# Función para mostrar la pantalla de inicio de sesión en la barra lateral
def mostrar_login():
    with st.sidebar:
        st.image('./fifa-logo.jpg', width=200)
        st.title("Inicio de Sesión")
        contraseña = st.text_input("Introduce la contraseña", type="password")
        if st.button("Iniciar sesión"):
            if contraseña == CONTRASEÑA_CORRECTA:
                st.session_state['sesion_iniciada'] = True
                st.success("Sesión iniciada correctamente.")
                st.stop()  # Detiene la ejecución
            else:
                st.error("Contraseña incorrecta. Acceso denegado.")

# Función para calcular el resultado
def calcular_resultado(preguntas, respuestas_usuario):
    respuestas_correctas = 0
    resultados = []
    feedback = []
    for i, pregunta in enumerate(preguntas):
        try:
            correct_indices = [pregunta['opciones'].index(resp) for resp in pregunta['respuestas_correctas']]
        except ValueError as e:
            st.error(f"Error en la pregunta {i + 1}: {str(e)}")
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

# Función para configurar el examen de prueba
def configurar_examen_prueba():
    if len(preguntas_prueba) < 20:
        st.error("No hay suficientes preguntas para generar un examen de prueba. Añade más preguntas.")
        return
    
    config = ExamConfig(num_preguntas=20, tiempo_limite=60, orden_aleatorio=True)
    exam_manager = ExamManager(config)
    st.session_state.exam_manager = exam_manager
    st.session_state.start_time = datetime.now()  # Start timer
    st.session_state.end_time = st.session_state.start_time + exam_manager.get_tiempo_limite()
    st.session_state.temas_seleccionados = []
    st.session_state.respuestas_usuario = []
    st.session_state.mostrar_resultados = False
    st.session_state.ver_correccion = False
    st.session_state.feedback = []
    st.session_state.preguntas = random.sample(preguntas_prueba, 20)  # Seleccionar 20 preguntas aleatorias
    st.session_state.modo_prueba = True
    st.stop()  # Detiene la ejecución

# Mostrar mensaje de bienvenida y tarifas si no se ha iniciado sesión
if not st.session_state['sesion_iniciada'] and not st.session_state['modo_prueba']:
    st.title("🌟 Prepárate para ser Agente FIFA ")
    st.markdown("""
        ### Bienvenido a la mejor aplicación de preparación para el examen de agente FIFA.
        Con nuestra plataforma podrás:
        - 🌍 **Acceder a preguntas actualizadas** sobre las normativas y reglas de la FIFA.
        - ⏱️ **Simular exámenes** con tiempo límite, como en el examen real.
        - 📊 **Más de 450 preguntas de Exámenes oficiales de FIFA.**
        
        ¡Inicia sesión y comienza a practicar ahora para asegurar tu éxito como agente FIFA!
    """)

    st.markdown("## 💰 Tarifas de Precios")
    st.markdown("""
    <style>
        .pricing-table {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }
        .pricing-card {
            background-color: #333;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            text-align: center;
            width: 200px;
            color: white;
            margin-bottom: 20px;
        }
        .pricing-card h2 {
            font-size: 24px;
            margin-bottom: 20px;
            color: white;
        }
        .pricing-card p {
            font-size: 32px;
            font-weight: bold;
            margin: 0;
            color: #ffd700;
        }
        .offer {
            color: #ff0000; /* Color rojo para la oferta */
            text-decoration: line-through; /* Texto tachado */
        }
    </style>
    <div class="pricing-table">
        <div class="pricing-card">
            <h2>Mensual</h2>
            <p>35€</p>
        </div>
        <div class="pricing-card">
            <h2>Trimestral</h2>
            <p><span class="offer">70€</span> 50€</p>
        </div>
        <div class="pricing-card">
            <h2>Anual</h2>
            <p>185€</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botón para hacer la prueba de examen
    if st.button("Hacer Prueba de Examen", key="prueba_examen"):
        configurar_examen_prueba()

    mostrar_login()  # Asegúrate de que esta función esté correctamente definida
else:
    # Aquí va el resto de tu lógica para manejar el examen
    if st.session_state['modo_prueba']:
        # Crear un formulario para el examen de prueba
        if not st.session_state.mostrar_resultados and not st.session_state.ver_correccion:
            with st.form("examen_prueba"):
                respuestas_usuario = []
                submit_attempted = False
                for i, pregunta in enumerate(st.session_state.preguntas):
                    st.markdown(f"### Pregunta {i + 1}")
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
                    respuestas_correctas, resultados, feedback = calcular_resultado(st.session_state.preguntas, respuestas_usuario)
                    st.session_state.respuestas_correctas = respuestas_correctas
                    st.session_state.resultados = resultados
                    st.session_state.feedback = feedback
                    st.session_state.mostrar_resultados = True
                    st.stop()  # Detiene la ejecución

        elif st.session_state.mostrar_resultados:
            # Mostrar resultado general
            if st.session_state.respuestas_correctas >= 15:
                st.markdown(
                    f"""
                    <div style='text-align: center; color: green;'>
                        <h2>🎉 ¡APTO! - Aciertos: {st.session_state.respuestas_correctas}/20</h2>
                        <p>¡Enhorabuena! Eres Agente FIFA</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style='text-align: center; color: red;'>
                        <h2>❌ NO APTO - Aciertos: {st.session_state.respuestas_correctas}/20</h2>
                        <p>Sigue practicando, ¡lo conseguirás!</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            if st.button("Ver corrección"):
                st.session_state.ver_correccion = True
                st.stop()  # Detiene la ejecución

        # Mostrar corrección detallada
        if st.session_state.ver_correccion:
            st.markdown("## Resultados del Examen")
            for idx, (pregunta, opciones, correct_indices, respuestas_usuario, es_correcta) in enumerate(st.session_state.resultados):
                st.markdown(f"### Pregunta {idx + 1}: {pregunta}")
                for i, opcion in enumerate(opciones):
                    if i in correct_indices:
                        st.markdown(f"- **{opcion}** :green_heart:")
                    elif respuestas_usuario[i] == 1:
                        st.markdown(f"- ~~{opcion}~~ :red_circle:")
                    else:
                        st.markdown(f"- {opcion}")
                st.markdown("---")

            st.markdown(f"### Resultado final: {'APTO' if st.session_state.respuestas_correctas >= 15 else 'NO APTO'} - Aciertos: {st.session_state.respuestas_correctas}/20")
