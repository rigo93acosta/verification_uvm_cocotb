"""
Demostración: ¿Por qué "0 × 100 = 0" es multiplicación por cero pero el modelo falla con "173 × 0"?
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor

print("\n" + "="*80)
print("  ¿Por qué el modelo falla con 173 × 0 si vio 0 × 100?")
print("="*80)

# ==============================================================================
# EXPERIMENTO: Entrenar solo con multiplicaciones donde a=0
# ==============================================================================

print("\n📚 DATOS DE ENTRENAMIENTO:")
print("─"*40)
train_data = [
    (0, 50),
    (0, 100),
    (0, 150),
    (0, 200),
    (50, 50),
    (100, 100),
]

for a, b in train_data:
    print(f"  {a:3d} × {b:3d} = {a*b:5d}")

print("\n⚠️  Nota: Todos los casos con cero tienen a=0 (primer número)")
print("         NO hay casos donde b=0 (segundo número)")

# Entrenar el modelo
X_train = np.array(train_data)
y_train = np.array([a * b for a, b in train_data])

rf = RandomForestRegressor(n_estimators=10, random_state=42, max_depth=5)
rf.fit(X_train, y_train)

# ==============================================================================
# PRUEBAS: Ver qué predice en diferentes casos
# ==============================================================================

print("\n\n🧪 PREDICCIONES DEL MODELO:")
print("="*80)

test_cases = [
    (0, 100, "Caso VISTO en entrenamiento"),
    (0, 173, "Similar a entrenamiento (a=0)"),
    (100, 0, "INVERTIDO: b=0 en lugar de a=0"),
    (173, 0, "INVERTIDO: b=0 con valor grande"),
]

for a, b, description in test_cases:
    real = a * b
    pred = rf.predict([[a, b]])[0]
    pred_int = int(round(pred))
    error = abs(pred_int - real)
    
    status = "✓" if error == 0 else "✗"
    print(f"\n{status} {a:3d} × {b:3d} = {real:5d}  (real)")
    print(f"  Predicción: {pred_int:5d}")
    print(f"  Error:      {error:5d}")
    print(f"  Nota:       {description}")
    
    if error > 0:
        print(f"  ❌ ¿Por qué falló?")
        if b == 0 and a != 0:
            print(f"     → El modelo NUNCA vio casos donde b=0")
            print(f"     → Solo aprendió: 'si a=0 → resultado=0'")
            print(f"     → NO aprendió: 'si b=0 → resultado=0'")
            print(f"     → Intenta adivinar basándose en que a={a} es grande")

# ==============================================================================
# EXPLICACIÓN VISUAL
# ==============================================================================

print("\n\n" + "="*80)
print("  EXPLICACIÓN: Por qué la posición importa")
print("="*80)

print("""
┌──────────────────────────────────────────────────────────────┐
│  Matemáticas (humanos):                                      │
│    0 × 100 = 100 × 0 = 0                                     │
│    ✓ Sabemos que la multiplicación es conmutativa            │
│                                                              │
│  Machine Learning (modelo):                                  │
│    [0, 100] → features diferentes que → [100, 0]            │
│    [a=0, b=100]                         [a=100, b=0]        │
│                                                              │
│    El modelo aprende PATRONES en los datos:                 │
│      - Vio muchos casos [0, X]                               │
│      - Aprendió: "cuando a=0, resultado=0"                   │
│                                                              │
│      - NO vio casos [X, 0]                                   │
│      - NO aprendió: "cuando b=0, resultado=0"                │
│                                                              │
│    Es como un estudiante que solo vio:                       │
│      "0 + cualquier_número = 0" (incorrecto, pero aprendió) │
│    Y nunca vio:                                              │
│      "cualquier_número + 0 = 0"                              │
└──────────────────────────────────────────────────────────────┘
""")

# ==============================================================================
# SOLUCIÓN
# ==============================================================================

print("\n" + "="*80)
print("  SOLUCIONES")
print("="*80)

print("""
1️⃣  Agregar datos simétricos en el entrenamiento:
   - Si incluyes (0, 100), también incluye (100, 0)
   - Si incluyes (5, 10), también incluye (10, 5)
   → El modelo aprenderá ambas reglas

2️⃣  Feature Engineering - agregar features simétricas:
   - En lugar de [a, b], usar [a, b, min(a,b), max(a,b)]
   - Agregar (a==0 OR b==0) como feature
   → Ayuda al modelo a capturar la simetría

3️⃣  Usar la solución correcta:
   - Para multiplicación: return a * b
   - No necesitas ML para esto
   → 100% preciso, instantáneo

El problema NO es que "0 × 100" no sea multiplicación por cero.
El problema es que el modelo no entiende que es LO MISMO que "100 × 0".
""")

print("\n" + "="*80 + "\n")
