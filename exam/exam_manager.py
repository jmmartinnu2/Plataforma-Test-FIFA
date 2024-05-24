import random
from datetime import datetime, timedelta
from examen_fifa import preguntas_por_categoria
from exam.config import ExamConfig

class ExamManager:
    def __init__(self, config=ExamConfig()):
        self.config = config
        self.preguntas = self.seleccionar_preguntas()

    def seleccionar_preguntas(self):
        todas_las_preguntas = []
        for categoria in preguntas_por_categoria.values():
            todas_las_preguntas.extend(categoria)
        if self.config.orden_aleatorio:
            random.shuffle(todas_las_preguntas)
        return random.sample(todas_las_preguntas, self.config.num_preguntas)

    def get_tiempo_limite(self):
        return timedelta(minutes=self.config.tiempo_limite)

    def __repr__(self):
        return f"ExamManager(config={self.config}, num_preguntas={len(self.preguntas)})"
