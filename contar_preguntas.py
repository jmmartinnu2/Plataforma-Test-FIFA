import re
from collections import Counter

# Ruta al archivo local
file_path = 'C:/Users/jmmar/Desktop/Plataforma-Test-FIFA/examen_fifa.py'

# Leer el archivo con la codificación utf-8
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
except UnicodeDecodeError:
    with open(file_path, 'r', encoding='latin-1') as file:
        content = file.read()

# Contar las ocurrencias de 'pregunta':
pattern = re.compile(r"'pregunta':\s*'([^']+)'")
matches = pattern.findall(content)

# Número total de preguntas
num_preguntas = len(matches)

# Contar preguntas repetidas
contador_preguntas = Counter(matches)
preguntas_repetidas = {pregunta: count for pregunta, count in contador_preguntas.items() if count > 1}

# Imprimir resultados
print(f"Número total de preguntas en el archivo: {num_preguntas}")
print("Preguntas repetidas y su frecuencia:")
for pregunta, count in preguntas_repetidas.items():
    print(f"{pregunta}: {count} veces")
