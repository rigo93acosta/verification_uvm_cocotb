# ml_agent.py
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class MLGuider:
    def __init__(self):
        # Usamos Random Forest para manejar múltiples variables
        self.model = RandomForestClassifier(n_estimators=10)
        self.X = [] # [data_in, c0, c1, c2]
        self.y = [] # ¿Hubo overflow?
        self.trained = False

    # def get_stimulus(self):
    #     if not self.trained:
    #         return np.random.randint(-128, 127, size=4)
        
    #     # Generamos 100 candidatos aleatorios y el modelo elige el mejor
    #     candidates = np.random.randint(-128, 127, size=(100, 4))
    #     probs_array = self.model.predict_proba(candidates)
    #     # Si solo hay una clase, predict_proba devuelve una sola columna
    #     if probs_array.shape[1] == 1:
    #         return np.random.randint(-128, 127, size=4)
    #     probs = probs_array[:, 1]
    #     return candidates[np.argmax(probs)]
    
    def get_stimulus(self):
        # Fase 1: Si no está entrenado, exploración pura
        if not self.trained:
            return np.random.randint(-128, 127, size=4)
        
        # Generamos candidatos para que el modelo evalúe
        candidates = np.random.randint(-128, 127, size=(100, 4))
        
        # Obtenemos probabilidades
        probs_matrix = self.model.predict_proba(candidates)
        
        # CORRECCIÓN TUYA APLICADA:
        # Verificamos si el modelo conoce la clase '1' (overflow)
        if probs_matrix.shape[1] < 2:
            # Si solo hay una columna, el modelo aún no sabe predecir fallos.
            # Seguimos explorando al azar dentro de los candidatos.
            return candidates[np.random.randint(0, 100)]
        
        # Fase 2: Explotación. Elegimos el candidato con mayor probabilidad de overflow (columna 1)
        probs_overflow = probs_matrix[:, 1]
        best_candidate_idx = np.argmax(probs_overflow)
        
        return candidates[best_candidate_idx]
    
    def record_result(self, stimulus, hit):
        self.X.append(stimulus)
        self.y.append(hit)
        if len(self.y) % 10 == 0: # Entrenar cada 10 muestras
            self.model.fit(self.X, self.y)
            self.trained = True