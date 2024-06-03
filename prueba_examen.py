import random

# Definimos dos conjuntos de preguntas de prueba
examen_prueba_1 = [
    {
        "pregunta": "¿Pregunta 1 del examen 1?",
        "opciones": ["Opción 1", "Opción 2", "Opción 3", "Opción 4"],
        "respuestas_correctas": ["Opción 1"]
    },
    # Añadir más preguntas aquí...
]

examen_prueba_2 = [
    {
        "pregunta": "¿Pregunta 1 del examen 2?",
        "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
        "respuestas_correctas": ["Opción A"]
    },
    # Añadir más preguntas aquí...
]

# Función para obtener un examen de prueba aleatorio
def obtener_examen_prueba():
    examenes = [examen_prueba_1, examen_prueba_2]
    return random.choice(examenes)
