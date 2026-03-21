"""
Explicación detallada: ¿Por qué fallan las predicciones de Random Forest?

Este script demuestra EXACTAMENTE por qué Random Forest predice valores incorrectos
incluso con R² alto.
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt

print("\n" + "="*80)
print("  ¿POR QUÉ RANDOM FOREST FALLA EN PREDICCIONES EXACTAS?")
print("="*80)

# ==============================================================================
# EJEMPLO 1: El problema fundamental - Promedio de árboles
# ==============================================================================
print("\n" + "#"*80)
print("#  EJEMPLO 1: Cómo funciona Random Forest internamente")
print("#"*80)

# Entrenar con pocos datos para ver el problema claramente
np.random.seed(42)
train_a = [0, 0, 50, 100, 150, 200, 255]
train_b = [0, 100, 50, 100, 150, 200, 255]
X_train = np.array([[a, b] for a, b in zip(train_a, train_b)])
y_train = np.array([a * b for a, b in zip(train_a, train_b)])

print(f"\nDatos de entrenamiento:")
for i, (a, b) in enumerate(zip(train_a, train_b)):
    print(f"  {a:3d} × {b:3d} = {y_train[i]:5d}")

# Crear Random Forest con solo 5 árboles para ver el efecto
rf = RandomForestRegressor(n_estimators=5, random_state=42, max_depth=10)
rf.fit(X_train, y_train)

# Caso problemático: 173 * 0 = 0
test_case = np.array([[173, 0]])
real_result = 173 * 0  # = 0

print(f"\n{'─'*80}")
print(f"CASO DE PRUEBA: 173 × 0 = {real_result} (valor real)")
print(f"{'─'*80}")

# Ver predicción de cada árbol individual
print(f"\nPredicciones de cada árbol en el bosque:")
tree_predictions = []
for i, tree in enumerate(rf.estimators_):
    pred = tree.predict(test_case)[0]
    tree_predictions.append(pred)
    print(f"  Árbol {i+1}: {pred:8.2f}")

# Promedio (predicción final)
rf_prediction = rf.predict(test_case)[0]
manual_avg = np.mean(tree_predictions)

print(f"\n{'─'*40}")
print(f"Promedio de árboles:  {manual_avg:8.2f}")
print(f"Predicción RF:        {rf_prediction:8.2f}")
print(f"Redondeado a entero:  {int(round(rf_prediction))}")
print(f"VALOR REAL:           {real_result}")
print(f"{'─'*40}")
print(f"\n❌ ERROR: {int(round(rf_prediction))} ≠ {real_result}")
print(f"   Diferencia: {abs(int(round(rf_prediction)) - real_result)}")

# ==============================================================================
# EJEMPLO 2: Por qué cada árbol da valores diferentes
# ==============================================================================
print("\n\n" + "#"*80)
print("#  EJEMPLO 2: ¿Por qué cada árbol predice algo diferente?")
print("#"*80)

print("""
Random Forest usa BOOTSTRAP SAMPLING:
  - Cada árbol se entrena con una muestra aleatoria CON reemplazo
  - Cada árbol puede ver datos diferentes
  - Cada árbol crea reglas (splits) diferentes
  
Para 173 × 0:
  - El modelo vio "0 × 100" pero NO vio "173 × 0"
  - Para ML, la POSICIÓN importa: [a, b] ≠ [b, a]
  - El árbol aprendió: "si a=0 → resultado=0"
  - Pero NO aprendió: "si b=0 → resultado=0"
  - Cuando ve a=173, b=0, interpola incorrectamente
""")

# Mostrar qué vio cada árbol
print(f"\nEjemplo de bootstrap samples (qué datos vio cada árbol):")
np.random.seed(42)
for tree_num in range(3):
    indices = np.random.choice(len(X_train), size=len(X_train), replace=True)
    print(f"\n  Árbol {tree_num+1} vio estos casos:")
    unique_indices = sorted(set(indices))
    for idx in unique_indices[:3]:  # Mostrar solo 3
        a, b = train_a[idx], train_b[idx]
        print(f"    {a:3d} × {b:3d} = {a*b:5d}")
    
    # Verificar si vio el caso específico b=0
    saw_b_zero = any(train_b[i] == 0 for i in indices)
    saw_a_zero = any(train_a[i] == 0 for i in indices)
    
    if not saw_b_zero:
        print(f"    ⚠️  Este árbol NO vio casos donde b=0 (segundo número es 0)")
    else:
        print(f"    ✓ Este árbol vio casos donde b=0")
    
    if saw_a_zero and not saw_b_zero:
        print(f"    → Sabe que a×0=0, pero NO sabe que 173×b=0 cuando b=0")

# ==============================================================================
# EJEMPLO 3: Visualización del problema de interpolación
# ==============================================================================
print("\n\n" + "#"*80)
print("#  EJEMPLO 3: Problema de interpolación")
print("#"*80)

# Entrenar con datos más realistas
np.random.seed(42)
n_samples = 100
train_a = np.random.randint(0, 256, n_samples)
train_b = np.random.randint(0, 256, n_samples)
X_train = np.array([[a, b] for a, b in zip(train_a, train_b)])
y_train = train_a * train_b

rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Casos de prueba problemáticos
test_cases = [
    (173, 0, "Multiplicación por 0"),
    (0, 173, "Multiplicación por 0 (invertido)"),
    (255, 255, "Máximo × Máximo"),
    (1, 1, "Mínimo × Mínimo"),
    (127, 128, "Valores medios"),
]

print(f"\n{'Caso':<30} {'Real':>10} {'Predicción':>12} {'Error':>10}")
print("─"*65)

errors = []
for a, b, description in test_cases:
    real = a * b
    pred = rf.predict([[a, b]])[0]
    pred_int = int(round(pred))
    error = abs(pred_int - real)
    errors.append(error)
    
    status = "✓" if error == 0 else "✗"
    print(f"{status} {description:<28} {real:>10} {pred_int:>12} {error:>10}")

print(f"\nError promedio: {np.mean(errors):.2f}")

# ==============================================================================
# EJEMPLO 4: Por qué R² es alto pero exactitud es baja
# ==============================================================================
print("\n\n" + "#"*80)
print("#  EJEMPLO 4: R² alto ≠ Predicciones exactas")
print("#"*80)

print("""
R² Score mide qué tan bien el modelo captura la TENDENCIA:
  - R² = 0.999 significa que el modelo explica 99.9% de la varianza
  - Pero NO significa que cada predicción sea exacta
  
Ejemplo:
  Real:        [100,  200,  300,  400,  500]
  Predicción:  [103,  198,  305,  398,  502]
  
  ✓ R² ≈ 0.999 (excelente correlación)
  ✗ Exactitud = 0% (ningún valor exacto)
""")

# Demostración
real_values = np.array([100, 200, 300, 400, 500, 1000, 2000, 5000, 10000])
predictions = real_values + np.random.normal(0, 50, len(real_values))  # Error ~50

from sklearn.metrics import r2_score
r2 = r2_score(real_values, predictions)
exact_matches = np.sum(np.round(predictions) == real_values)

print(f"\nEjemplo numérico:")
print(f"  R² Score:         {r2:.6f}  ✓ Excelente")
print(f"  Exactitud:        {exact_matches}/{len(real_values)} = {exact_matches/len(real_values)*100:.0f}%  ✗ Terrible")

# ==============================================================================
# EJEMPLO 5: El problema del redondeo
# ==============================================================================
print("\n\n" + "#"*80)
print("#  EJEMPLO 5: El problema del redondeo")
print("#"*80)

print("""
Random Forest predice valores CONTINUOS (float), no enteros.
Al redondear a entero, pequeños errores se amplifican:

  Real:        7992
  Predicción:  7992.3  →  round() → 7992  ✓ Correcto
  Predicción:  7992.6  →  round() → 7993  ✗ Error de 1
  Predicción:  8050.2  →  round() → 8050  ✗ Error de 58
""")

# Casos reales del log anterior
real_errors = [
    ("173 × 0", 0, 23, "Interpolación incorrecta"),
    ("195 × 247", 48165, 48450, "Error de redondeo grande"),
    ("100 × 151", 15100, 15403, "Error de interpolación"),
    ("147 × 100", 14700, 14709, "Error pequeño de redondeo"),
]

print(f"\n{'Operación':<12} {'Real':>10} {'Predicción':>12} {'Error':>8} {'Causa':<30}")
print("─"*80)
for op, real, pred, cause in real_errors:
    error = abs(pred - real)
    pct = (error / max(real, 1)) * 100
    print(f"{op:<12} {real:>10} {pred:>12} {error:>8} ({pct:5.2f}%)  {cause}")

# ==============================================================================
# SOLUCIÓN
# ==============================================================================
print("\n\n" + "="*80)
print("  SOLUCIÓN: ¿Cómo arreglar esto?")
print("="*80)

print("""
Opción 1: MÁS DATOS de entrenamiento
  - 100 muestras   → ~1% exactitud
  - 1,000 muestras → ~1-2% exactitud
  - 10,000 muestras → ~5-10% exactitud
  - 65,536 muestras (exhaustivo) → ~15-20% exactitud
  
Opción 2: MEJOR MODELO
  - Neural Network con muchas capas
  - Gradient Boosting (XGBoost, LightGBM)
  - Tabla de lookup para casos comunes
  
Opción 3: MEJOR SOLUCIÓN - No usar ML
  - Para multiplicación: usar directamente a × b
  - ML es para funciones COMPLEJAS donde no conoces la fórmula
  - Ejemplo: Comportamiento de un filtro FIR, protocolo complejo, etc.

¿Cuándo SÍ usar ML en verificación?
  ✓ Funciones no-determinísticas o complejas
  ✓ Sistemas con muchas variables interdependientes
  ✓ Cuando no tienes un modelo matemático simple
  ✓ Para detectar anomalías en comportamiento esperado
  
¿Cuándo NO usar ML?
  ✗ Funciones matemáticas determinísticas simples (suma, mult, etc)
  ✗ Cuando tienes la fórmula exacta
  ✗ Cuando necesitas 100% de precisión
""")

print("\n" + "="*80)
print("  FIN DE LA EXPLICACIÓN")
print("="*80 + "\n")
