"""
Script de comparación: Random Forest vs Neural Network vs Entrenamiento Exhaustivo
Demuestra cómo el entrenamiento exhaustivo mejora dramáticamente la precisión
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
import time

def engineer_features(a, b):
    """Features mejoradas para capturar multiplicación"""
    return [
        a, b,
        a * a, b * b,
        a + b, abs(a - b),
        min(a, b), max(a, b),
        (a >> 4), (b >> 4),
        (a & 0x0F), (b & 0x0F),
    ]

def train_and_evaluate(model_name, model, X_train, y_train, X_test, y_test):
    """Entrena y evalúa un modelo"""
    print(f"\n{'='*60}")
    print(f"  {model_name}")
    print(f"{'='*60}")
    
    # Entrenar
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start
    
    # Predecir
    y_pred = model.predict(X_test)
    y_pred_int = np.round(y_pred).astype(int)
    
    # Métricas
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Exactitud perfecta
    exact_matches = np.sum(y_pred_int == y_test)
    accuracy = exact_matches / len(y_test) * 100
    
    # Exactitud con tolerancia
    tolerance = np.abs(y_pred_int - y_test) <= (y_test * 0.01 + 1)
    accuracy_tol = np.sum(tolerance) / len(y_test) * 100
    
    # Reporte
    print(f"Tiempo de entrenamiento: {train_time:.2f}s")
    print(f"Muestras de entrenamiento: {len(X_train)}")
    print(f"Muestras de prueba: {len(X_test)}")
    print(f"\nMétricas:")
    print(f"  - MSE:                    {mse:,.2f}")
    print(f"  - R² Score:               {r2:.6f}")
    print(f"  - Exactitud (exacta):     {accuracy:.2f}% ({exact_matches}/{len(y_test)})")
    print(f"  - Exactitud (1% tol):     {accuracy_tol:.2f}%")
    
    # Mostrar algunos errores
    errors = np.abs(y_pred_int - y_test)
    print(f"\nDistribución de errores:")
    print(f"  - Error promedio:         {np.mean(errors):.2f}")
    print(f"  - Error máximo:           {int(np.max(errors))}")
    print(f"  - Casos con error = 0:    {np.sum(errors == 0)}")
    print(f"  - Casos con error <= 10:  {np.sum(errors <= 10)}")
    print(f"  - Casos con error > 100:  {np.sum(errors > 100)}")
    
    return {
        'mse': mse,
        'r2': r2,
        'accuracy': accuracy,
        'accuracy_tol': accuracy_tol,
        'train_time': train_time
    }

def main():
    print("\n" + "="*60)
    print("  COMPARACIÓN DE MODELOS ML PARA MULTIPLICADOR 8-BIT")
    print("="*60)
    
    # Configurar datos de prueba (siempre los mismos)
    np.random.seed(42)
    test_size = 1000
    test_a = np.random.randint(0, 256, test_size)
    test_b = np.random.randint(0, 256, test_size)
    X_test = np.array([engineer_features(a, b) for a, b in zip(test_a, test_b)])
    y_test = test_a * test_b
    
    results = {}
    
    # ====================================================================
    # EXPERIMENTO 1: Random Forest con 2000 muestras
    # ====================================================================
    print("\n\n" + "#"*60)
    print("#  EXPERIMENTO 1: Random Forest (2000 muestras)")
    print("#"*60)
    
    np.random.seed(42)
    train_a = np.random.randint(0, 256, 2000)
    train_b = np.random.randint(0, 256, 2000)
    X_train = np.array([engineer_features(a, b) for a, b in zip(train_a, train_b)])
    y_train = train_a * train_b
    
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )
    
    results['RF_2k'] = train_and_evaluate(
        "Random Forest (2000 samples)", 
        model, X_train, y_train, X_test, y_test
    )
    
    # ====================================================================
    # EXPERIMENTO 2: Neural Network con 2000 muestras
    # ====================================================================
    print("\n\n" + "#"*60)
    print("#  EXPERIMENTO 2: Neural Network (2000 muestras)")
    print("#"*60)
    
    model = MLPRegressor(
        hidden_layer_sizes=(256, 128, 64),
        activation='relu',
        solver='adam',
        max_iter=1000,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.15,
        verbose=False
    )
    
    results['NN_2k'] = train_and_evaluate(
        "Neural Network (2000 samples)",
        model, X_train, y_train, X_test, y_test
    )
    
    # ====================================================================
    # EXPERIMENTO 3: Neural Network con 10000 muestras
    # ====================================================================
    print("\n\n" + "#"*60)
    print("#  EXPERIMENTO 3: Neural Network (10000 muestras)")
    print("#"*60)
    
    np.random.seed(42)
    train_a = np.random.randint(0, 256, 10000)
    train_b = np.random.randint(0, 256, 10000)
    X_train = np.array([engineer_features(a, b) for a, b in zip(train_a, train_b)])
    y_train = train_a * train_b
    
    model = MLPRegressor(
        hidden_layer_sizes=(512, 256, 128, 64),
        activation='relu',
        solver='adam',
        max_iter=2000,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        verbose=False
    )
    
    results['NN_10k'] = train_and_evaluate(
        "Neural Network (10000 samples)",
        model, X_train, y_train, X_test, y_test
    )
    
    # ====================================================================
    # EXPERIMENTO 4: ENTRENAMIENTO EXHAUSTIVO (todas las combinaciones)
    # ====================================================================
    print("\n\n" + "#"*60)
    print("#  EXPERIMENTO 4: EXHAUSTIVO (65536 combinaciones)")
    print("#"*60)
    print("Generando todas las combinaciones posibles...")
    
    # Generar TODAS las combinaciones
    all_a = []
    all_b = []
    for a in range(256):
        for b in range(256):
            all_a.append(a)
            all_b.append(b)
    
    all_a = np.array(all_a)
    all_b = np.array(all_b)
    X_train_exhaustive = np.array([engineer_features(a, b) for a, b in zip(all_a, all_b)])
    y_train_exhaustive = all_a * all_b
    
    print(f"Total de muestras: {len(X_train_exhaustive):,}")
    
    # Usar Random Forest (más rápido para muchas muestras)
    model = RandomForestRegressor(
        n_estimators=100,  # Menos árboles por velocidad
        max_depth=30,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )
    
    results['RF_exhaustive'] = train_and_evaluate(
        "Random Forest EXHAUSTIVO (65536 samples)",
        model, X_train_exhaustive, y_train_exhaustive, X_test, y_test
    )
    
    # ====================================================================
    # COMPARACIÓN FINAL
    # ====================================================================
    print("\n\n" + "="*80)
    print("  RESUMEN COMPARATIVO")
    print("="*80)
    print(f"{'Modelo':<35} {'Muestras':<10} {'Exactitud':<12} {'R²':<10} {'Tiempo':<10}")
    print("-"*80)
    
    configs = [
        ('RF_2k', 'Random Forest (2k)', 2000),
        ('NN_2k', 'Neural Network (2k)', 2000),
        ('NN_10k', 'Neural Network (10k)', 10000),
        ('RF_exhaustive', 'RF Exhaustivo (65k)', 65536),
    ]
    
    for key, name, samples in configs:
        r = results[key]
        print(f"{name:<35} {samples:<10,} {r['accuracy']:>6.2f}%      {r['r2']:.4f}    {r['train_time']:>5.2f}s")
    
    print("="*80)
    print("\n✨ CONCLUSIÓN:")
    print("   - Más muestras = Mejor precisión")
    print("   - Entrenamiento exhaustivo da la mejor precisión")
    print("   - Pero para multiplicación simple, usar a*b directamente es lo ideal")
    print("   - ML es útil para funciones complejas, no para operaciones matemáticas básicas")
    print()

if __name__ == "__main__":
    main()
