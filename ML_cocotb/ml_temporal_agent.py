import numpy as np
from sklearn.ensemble import RandomForestRegressor
from collections import deque

class TemporalMLGuider:
    def __init__(self, history_depth=3):
        """
        history_depth: Cuántos pasos hacia atrás recordar. 
        Para un filtro de 3 taps, necesitamos al menos los últimos 2 valores + el actual.
        """
        self.history_depth = history_depth
        
        # Buffer para guardar las entradas anteriores (iniciamos con ceros)
        self.input_history = deque([0]*history_depth, maxlen=history_depth)
        
        # Modelo de Regresión
        self.model = RandomForestRegressor(n_estimators=20, random_state=42)
        
        # Dataset de entrenamiento
        self.X_train = [] 
        self.y_train = []
        self.trained = False
        self.cycle_count = 0

    def get_stimulus(self, current_coeffs):
        """
        Propone el siguiente 'data_in' basado en la historia y los coeficientes actuales.
        Retorna: (best_data_in, full_feature_vector)
        """
        # Fase 1: Exploración (o si hay pocos datos)
        if not self.trained or np.random.rand() < 0.15: # 15% exploración forzada
            return np.random.randint(-128, 127)

        # Fase 2: Explotación Inteligente
        # Generamos 100 candidatos posibles para el "siguiente valor"
        candidates = np.random.randint(-128, 127, size=100)
        
        # Construimos la matriz de características para los candidatos:
        # Cada fila será: [Candidato, Historia_t-1, Historia_t-2, Coef0, Coef1, Coef2]
        # Nota: La historia es FIJA para todos los candidatos en este ciclo.
        history_features = list(self.input_history)[:-1] # Tomamos t-1 y t-2
        
        # Creamos una matriz donde repetimos la historia y coeficientes para cada candidato
        base_features = history_features + list(current_coeffs)
        candidate_matrix = []
        
        for cand in candidates:
            # Feature Vector: [Candidato_Actual] + [Historia Pasada] + [Coeficientes]
            row = [cand] + base_features
            candidate_matrix.append(row)
            
        candidate_matrix = np.array(candidate_matrix)

        # El modelo predice la magnitud de salida para cada candidato
        predictions = self.model.predict(candidate_matrix)
        
        # Elegimos el candidato que promete la mayor salida
        best_idx = np.argmax(predictions)
        return candidates[best_idx]

    def record_result(self, data_in_used, coeffs_used, output_magnitude):
        """
        Guarda lo que realmente pasó para entrenar al modelo.
        """
        # 1. Recuperamos la historia que existía ANTES de este nuevo dato
        # (Como deque se actualiza al final, aquí reconstruimos el vector de tiempo t)
        history_features = list(self.input_history)[:-1]
        
        # 2. Construimos el vector de características completo:
        # [Entrada_Usada, t-1, t-2, Coeffs...]
        features = [data_in_used] + history_features + list(coeffs_used)
        
        self.X_train.append(features)
        self.y_train.append(output_magnitude)
        
        # 3. ACTUALIZAMOS LA MEMORIA con el dato nuevo
        self.input_history.appendleft(data_in_used)
        
        self.cycle_count += 1

        # Re-entrenamos cada 50 ciclos para no hacerlo muy lento
        if self.cycle_count >= 50 and self.cycle_count % 50 == 0:
            self.model.fit(self.X_train, self.y_train)
            self.trained = True