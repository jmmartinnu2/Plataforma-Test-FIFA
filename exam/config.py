class ExamConfig:
    def __init__(self, num_preguntas=20, tiempo_limite=60, orden_aleatorio=True):
        self.num_preguntas = num_preguntas
        self.tiempo_limite = tiempo_limite  # Tiempo límite en minutos
        self.orden_aleatorio = orden_aleatorio

    def __repr__(self):
        return f"ExamConfig(num_preguntas={self.num_preguntas}, tiempo_limite={self.tiempo_limite}, orden_aleatorio={self.orden_aleatorio})"
