import random
from datetime import datetime, timedelta
import pandas as pd
import os

# **1. Configuración de la Página**
import streamlit as st
st.set_page_config(page_title="Examen FIFA", layout="centered")

# **2. Importar `st_autorefresh`**
try:
    from streamlit import st_autorefresh
    autorefresh_available = True
except ImportError:
    autorefresh_available = False
    st.error("❌ La función 'st_autorefresh' no está disponible en esta versión de Streamlit. Por favor, actualiza Streamlit ejecutando `pip install --upgrade streamlit`.")

# **Importar tus módulos personalizados (asegúrate de que las rutas son correctas)**
# Reemplaza estos import según la estructura de tu proyecto
# from examen_fifa import preguntas_por_categoria
# from exam.config import ExamConfig
# from exam.exam_manager import ExamManager
# from exam.reports import guardar_resultado_examen, obtener_historial_examenes, obtener_detalles_examen
# from examen_prueba import preguntas_prueba

# **Simulación de módulos personalizados para este ejemplo**
# Elimina estas definiciones si ya tienes tus propios módulos
preguntas_por_categoria = {
    "Reglas Básicas": [
        {
            "pregunta": "¿Cuántos jugadores conforman un equipo en el campo durante un partido de fútbol?",
            "opciones": ["9", "10", "11", "12"],
            "respuestas_correctas": ["11"]
        },
        # Añade más preguntas según sea necesario
    ],
    # Añade más categorías según sea necesario
}

preguntas_prueba = preguntas_por_categoria["Reglas Básicas"]  # Simplificación para el ejemplo

# **3. Definir Constantes y Inicializar el Estado de la Sesión**
CONTRASEÑA_CORRECTA = "091086"

# Inicializar el estado de la sesión
if 'sesion_iniciada' not in st.session_state:
    st.session_state['sesion_iniciada'] = False

if 'modo_prueba' not in st.session_state:
    st.session_state['modo_prueba'] = False

if 'historial_preguntas' not in st.session_state:
    st.session_state['historial_preguntas'] = []

if 'mostrar_resultados' not in st.session_state:
    st.session_state['mostrar_resultados'] = False

if 'ver_correccion' not in st.session_state:
    st.session_state['ver_correccion'] = False

if 'respuestas_correctas' not in st.session_state:
    st.session_state['respuestas_correctas'] = 0

if 'resultados' not in st.session_state:
    st.session_state['resultados'] = []

if 'feedback' not in st.session_state:
    st.session_state['feedback'] = []

if 'exam_manager' not in st.session_state:
    st.session_state['exam_manager'] = None

if 'preguntas' not in st.session_state:
    st.session_state['preguntas'] = []

if 'end_time' not in st.session_state:
    st.session_state['end_time'] = None

# Crear el directorio data si no existe
if not os.path.exists('data'):
    os.makedirs('data')

# **4. Función Auxiliar para Rerun**
def rerun_app():
    try:
        st.experimental_rerun()
    except Exception:
        pass

# **5. Función para Mostrar la Pantalla de Inicio de Sesión en la Barra Lateral**
def mostrar_login():
    with st.sidebar:
        st.image('./fifa-logo.jpg', width=200)  # Asegúrate de tener la imagen en el directorio correcto
        st.title("Inicio de Sesión")
        contraseña = st.text_input("Introduce la contraseña", type="password")
        if st.button("Iniciar sesión", key="boton_iniciar_sesion"):
            if contraseña == CONTRASEÑA_CORRECTA:
                st.session_state['sesion_iniciada'] = True
                st.success("✅ Sesión iniciada correctamente.")
                rerun_app()  # Actualiza la interfaz
            else:
                st.error("❌ Contraseña incorrecta. Acceso denegado.")

# **6. Función para Calcular el Resultado**
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
        usuario_correcto = [1 if idx in correct_indices else 0 for idx in range(len(pregunta['opciones']))]
        es_correcta = respuestas_usuario[i] == usuario_correcto
        if es_correcta:
            respuestas_correctas += 1
            feedback.append((pregunta['pregunta'], "Respuesta correcta"))
        else:
            feedback.append((pregunta['pregunta'], "Respuesta incorrecta", pregunta['respuestas_correctas']))
        resultados.append((pregunta['pregunta'], pregunta['opciones'], correct_indices, respuestas_usuario[i], es_correcta))
    return respuestas_correctas, resultados, feedback

# **7. Función para Seleccionar Preguntas Basadas en Temas**
def seleccionar_preguntas_por_temas(preguntas_por_categoria, temas_seleccionados, num_preguntas, historial_preguntas):
    todas_las_preguntas = []
    if not temas_seleccionados:  # Si no se seleccionan temas, usar todas las preguntas
        for categoria in preguntas_por_categoria.values():
            todas_las_preguntas.extend(categoria)
    else:
        for tema in temas_seleccionados:
            todas_las_preguntas.extend(preguntas_por_categoria.get(tema, []))
    
    # Excluir preguntas que han sido usadas en los últimos dos exámenes
    preguntas_disponibles = [p for p in todas_las_preguntas if p['pregunta'] not in historial_preguntas]
    
    # Verificar si hay suficientes preguntas disponibles
    if len(preguntas_disponibles) < num_preguntas:
        st.warning(f"No hay suficientes preguntas disponibles para los temas seleccionados. Máximo disponible: {len(preguntas_disponibles)}")
        return []
    
    # Seleccionar preguntas sin reemplazo
    preguntas_seleccionadas = random.sample(preguntas_disponibles, num_preguntas)
    
    return preguntas_seleccionadas

# **8. Función para Actualizar el Historial de Preguntas**
def actualizar_historial_preguntas(nuevas_preguntas, num_preguntas):
    st.session_state['historial_preguntas'].extend(nuevas_preguntas)
    # Mantener solo las preguntas de los últimos dos exámenes
    if len(st.session_state['historial_preguntas']) > 2 * num_preguntas:
        st.session_state['historial_preguntas'] = st.session_state['historial_preguntas'][-2 * num_preguntas:]

# **9. Función para Actualizar el Temporizador**
def actualizar_temporizador():
    now = datetime.now()
    remaining_time = st.session_state['end_time'] - now
    remaining_seconds = int(remaining_time.total_seconds())
    
    if remaining_seconds > 0:
        minutes, seconds = divmod(remaining_seconds, 60)
        # Mostrar el temporizador en grande en la pantalla principal
        st.markdown(
            f"""
            <h1 style='text-align: center; font-size: 72px;'>
                ⏳ Tiempo restante: {minutes:02}:{seconds:02}
            </h1>
            """,
            unsafe_allow_html=True
        )
        # Mostrar el temporizador en la barra lateral
        st.sidebar.markdown(
            f"""
            <h2 style='text-align: center;'>
                ⏳ {minutes:02}:{seconds:02}
            </h2>
            """,
            unsafe_allow_html=True
        )
        if minutes < 5:
            st.sidebar.warning("⚠️ Quedan menos de 5 minutos.")
        return True
    else:
        st.markdown(
            f"""
            <h1 style='text-align: center; font-size: 72px; color: red;'>
                ❌ Tiempo terminado
            </h1>
            """,
            unsafe_allow_html=True
        )
        st.sidebar.warning("⏰ Tiempo terminado")
        st.session_state['mostrar_resultados'] = True
        return False

# **10. Función para Configurar el Examen de Prueba**
def configurar_examen_prueba():
    if len(preguntas_prueba) < 20:
        st.error("❌ No hay suficientes preguntas para generar un examen de prueba. Añade más preguntas.")
        return
    
    config = {
        'num_preguntas': 20,
        'tiempo_limite': 60,  # minutos
        'orden_aleatorio': True,
        'temas_seleccionados': []  # Sin temas específicos para la prueba
    }
    exam_manager = None  # Simplificación para el ejemplo
    st.session_state['exam_manager'] = exam_manager
    st.session_state['start_time'] = datetime.now()  # Iniciar temporizador
    st.session_state['end_time'] = st.session_state['start_time'] + timedelta(minutes=config['tiempo_limite'])
    st.session_state['temas_seleccionados'] = config['temas_seleccionados']
    st.session_state['respuestas_usuario'] = []
    st.session_state['mostrar_resultados'] = False
    st.session_state['ver_correccion'] = False
    st.session_state['feedback'] = []
    st.session_state['preguntas'] = random.sample(preguntas_prueba, config['num_preguntas'])  # Seleccionar preguntas aleatorias
    st.session_state['modo_prueba'] = True
    rerun_app()  # Actualiza la interfaz

# **11. Función para Iniciar el Examen (Modo Normal)**
def iniciar_examen_normal(num_preguntas, tiempo_limite, orden_aleatorio, temas_seleccionados):
    config = {
        'num_preguntas': num_preguntas,
        'tiempo_limite': tiempo_limite,  # minutos
        'orden_aleatorio': orden_aleatorio,
        'temas_seleccionados': temas_seleccionados
    }
    exam_manager = None  # Simplificación para el ejemplo
    st.session_state['exam_manager'] = exam_manager
    st.session_state['start_time'] = datetime.now()  # Iniciar temporizador
    st.session_state['end_time'] = st.session_state['start_time'] + timedelta(minutes=tiempo_limite)
    st.session_state['temas_seleccionados'] = temas_seleccionados
    st.session_state['respuestas_usuario'] = []
    st.session_state['mostrar_resultados'] = False
    st.session_state['ver_correccion'] = False
    st.session_state['feedback'] = []
    st.session_state['preguntas'] = seleccionar_preguntas_por_temas(
        preguntas_por_categoria,
        temas_seleccionados,
        num_preguntas,
        st.session_state['historial_preguntas']
    )
    if st.session_state['preguntas']:  # Verifica si se seleccionaron preguntas
        actualizar_historial_preguntas([p['pregunta'] for p in st.session_state['preguntas']], num_preguntas)
    rerun_app()  # Actualiza la interfaz

# **12. Función para Guardar y Obtener Detalles del Examen**
# Asegúrate de implementar estas funciones según tu lógica de almacenamiento
def guardar_resultado_examen(usuario_id, fecha, estado, aciertos, total_preguntas, resultados):
    # Implementa la lógica para guardar los resultados del examen
    pass

def obtener_detalles_examen(examen_id):
    # Implementa la lógica para obtener detalles de un examen específico
    pass

# **13. Lógica Principal de la Aplicación**
if not st.session_state['sesion_iniciada'] and not st.session_state['modo_prueba'] and not st.session_state['exam_manager']:
    st.title("🌟 Prepárate para ser Agente FIFA")
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

    # Mostrar la pantalla de inicio de sesión
    mostrar_login()

else:
    # Opciones de navegación después de iniciar sesión
    opcion = st.sidebar.selectbox(
        "📂 Selecciona una opción",
        ["📋 Configurar Examen", "🚀 Iniciar Examen", "🔍 Resultados Detallados"],
        key="nav_selectbox_main"
    )

    if opcion == "📋 Configurar Examen":
        # Configuración del examen
        st.title("📝 Configuración del Examen")
        num_preguntas = st.number_input("Número de Preguntas", min_value=1, max_value=100, value=20)
        tiempo_limite = st.number_input("Tiempo Límite (minutos)", min_value=1, max_value=180, value=60)
        orden_aleatorio = st.checkbox("🔀 Orden Aleatorio de Preguntas", value=True)

        temas = list(preguntas_por_categoria.keys())
        temas_seleccionados = st.multiselect("📚 Selecciona los temas", temas, default=temas)

        if st.button("Guardar Configuración", key="guardar_configuracion_button"):
            st.session_state['configuracion_examen'] = {
                'num_preguntas': num_preguntas,
                'tiempo_limite': tiempo_limite,
                'orden_aleatorio': orden_aleatorio,
                'temas_seleccionados': temas_seleccionados
            }
            st.success("✅ Configuración guardada.")

    if opcion == "🚀 Iniciar Examen":
        if 'configuracion_examen' not in st.session_state:
            st.warning("⚠️ Primero configura el examen en la opción '📋 Configurar Examen'.")
        else:
            config = st.session_state['configuracion_examen']
            iniciar_examen_normal(
                config['num_preguntas'],
                config['tiempo_limite'],
                config['orden_aleatorio'],
                config['temas_seleccionados']
            )

    if st.session_state['exam_manager']:
        # **Implementación del Temporizador con `st_autorefresh`**
        if autorefresh_available:
            # Añadir st_autorefresh para actualizar la aplicación cada segundo
            st_autorefresh(interval=1000, key="examen_autorefresh")
        else:
            st.warning("El temporizador no se actualizará automáticamente porque 'st_autorefresh' no está disponible.")

        # Actualizar y mostrar el temporizador
        if st.session_state['end_time']:
            actualizar_temporizador()

        # Mostrar las preguntas sin usar st.form
        if not st.session_state['mostrar_resultados'] and not st.session_state['ver_correccion']:
            respuestas_usuario = []
            for i, pregunta in enumerate(st.session_state['preguntas']):
                st.markdown(f"### Pregunta {i + 1}")
                st.markdown(f"**{pregunta['pregunta']}**")
                selected_options = []
                for j, opt in enumerate(pregunta['opciones']):
                    key = f"q{i}_opt{j}"
                    selected = st.checkbox(opt, key=key)
                    selected_options.append(selected)
                respuestas_usuario.append(selected_options)
                st.markdown("---")  # Añadir una línea divisoria entre preguntas

            # Botón para enviar examen
            if st.button("✅ Enviar Examen", key="submit_examen"):
                # Verificar si el tiempo ha expirado
                now = datetime.now()
                if now >= st.session_state['end_time']:
                    st.warning("⏰ El tiempo ha expirado. No puedes enviar el examen.")
                    st.session_state['mostrar_resultados'] = True
                else:
                    # Validar las respuestas del usuario
                    sin_responder = [i + 1 for i, options in enumerate(respuestas_usuario) if not any(options)]
                    if sin_responder:
                        st.warning("⚠️ Debes seleccionar al menos una opción para cada pregunta.")
                    else:
                        st.session_state['respuestas_usuario'] = respuestas_usuario
                        respuestas_usuario_flat = [[1 if opt else 0 for opt in q] for q in respuestas_usuario]
                        respuestas_correctas, resultados, feedback = calcular_resultado(st.session_state['preguntas'], respuestas_usuario_flat)
                        st.session_state['respuestas_correctas'] = respuestas_correctas
                        st.session_state['resultados'] = resultados
                        st.session_state['feedback'] = feedback
                        st.session_state['mostrar_resultados'] = True
                        guardar_resultado_examen(
                            0,  # Asignar un id por defecto ya que no hay usuario
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'APTO' if respuestas_correctas >= 15 else 'NO APTO',
                            respuestas_correctas,
                            len(st.session_state['preguntas']),
                            resultados
                        )
                        rerun_app()

    elif st.session_state['mostrar_resultados']:
        # Mostrar resultado general
        if st.session_state['respuestas_correctas'] >= 15:
            st.markdown(
                f"""
                <div style='text-align: center; color: green;'>
                    <h2>🎉 ¡APTO! - Aciertos: {st.session_state['respuestas_correctas']}/{len(st.session_state['preguntas'])}</h2>
                    <p>¡Enhorabuena! Eres Agente FIFA</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='text-align: center; color: red;'>
                    <h2>❌ NO APTO - Aciertos: {st.session_state['respuestas_correctas']}/{len(st.session_state['preguntas'])}</h2>
                    <p>Sigue practicando, ¡lo conseguirás!</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        if st.button("🔍 Ver Corrección", key="ver_correccion_button_main"):
            st.session_state['ver_correccion'] = True
            rerun_app()

    # Mostrar corrección detallada
    if st.session_state.get('ver_correccion', False):
        st.markdown("## 📑 Resultados del Examen")
        for idx, (pregunta, opciones, correct_indices, respuestas_usuario, es_correcta) in enumerate(st.session_state['resultados']):
            st.markdown(f"### Pregunta {idx + 1}: {pregunta}")
            for i, opcion in enumerate(opciones):
                if i in correct_indices:
                    st.markdown(f"- **{opcion}** ✅")
                elif respuestas_usuario[i] == 1:
                    st.markdown(f"- ~~{opcion}~~ ❌")
                else:
                    st.markdown(f"- {opcion}")
            st.markdown("---")

        st.markdown(f"### Resultado final: {'✅ APTO' if st.session_state['respuestas_correctas'] >= 15 else '❌ NO APTO'} - Aciertos: {st.session_state['respuestas_correctas']}/{len(st.session_state['preguntas'])}")

        if st.button("🚀 Iniciar Nuevo Examen", key="boton_iniciar_examen_correcion_final"):
            # Reiniciar las variables necesarias en st.session_state
            st.session_state['mostrar_resultados'] = False
            st.session_state['ver_correccion'] = False
            st.session_state['exam_manager'] = None
            st.session_state['preguntas'] = []
            st.session_state['respuestas_usuario'] = []
            st.session_state['respuestas_correctas'] = 0
            st.session_state['resultados'] = []
            st.session_state['feedback'] = []
            st.session_state['modo_prueba'] = False
            st.session_state['end_time'] = None

            rerun_app()

    # **14. Añadir Banner de Contacto por WhatsApp**
    st.sidebar.markdown(
        """
        ---
        ### 📞 Contacta con Nosotros
        Para más información, puedes contactarnos directamente por WhatsApp.
        """
    )

    st.sidebar.markdown(
        """
        <a href="https://wa.me/34645764853" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20" style="margin-right: 10px;"> +34 645 764 853
        </a>
        """,
        unsafe_allow_html=True
    )
