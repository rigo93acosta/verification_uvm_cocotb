import numpy as np
from sklearn.ensemble import RandomForestRegressor 

class MLGuider:
    def __init__(self):
        # Usamos Regressor para predecir la magnitud de la salida
        self.model = RandomForestRegressor(n_estimators=10)
        self.X = [] 
        self.y = [] # Ahora 'y' será la magnitud absoluta de la salida (abs(data_out))
        self.trained = False

    def get_stimulus(self):
        # Fase 1: Exploración pura si no hay suficientes datos
        if not self.trained:
            return np.random.randint(-128, 127, size=4)
        
        # Generamos candidatos aleatorios
        candidates = np.random.randint(-128, 127, size=(100, 4))
        
        # PREDICCIÓN: El modelo predice qué valor de salida producirá cada candidato
        predicted_magnitudes = self.model.predict(candidates)
        
        # ELEGIR: Tomamos el candidato que el modelo cree que dará el valor más alto
        best_candidate_idx = np.argmax(predicted_magnitudes)
        
        # Un toque de aleatoriedad (Epsilon-Greedy) para no estancarse en máximos locales
        if np.random.rand() < 0.1: # 10% de las veces elige al azar
            return candidates[np.random.randint(0, 100)]
            
        return candidates[best_candidate_idx]

    def record_result(self, stimulus, output_magnitude):
        self.X.append(stimulus)
        self.y.append(output_magnitude) # Guardamos qué tan grande fue la salida
        
        if len(self.y) >= 10 and len(self.y) % 10 == 0:
            self.model.fit(self.X, self.y)
            self.trained = True