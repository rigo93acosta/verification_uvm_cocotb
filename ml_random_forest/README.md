# Random Forest ML-based Verification for 8-bit Multiplier

## 📋 Descripción

Este proyecto demuestra la verificación funcional de un multiplicador de 8 bits utilizando **Random Forest** (Bosque Aleatorio) como agente de machine learning. El enfoque utiliza scikit-learn para entrenar un modelo que aprende el comportamiento del multiplicador y luego lo usa para verificar su correctitud.

## 🎯 Objetivo

Demostrar cómo Random Forest puede ser utilizado en la verificación de hardware para:
- Aprender el comportamiento esperado del DUT (Device Under Test)
- Predecir resultados esperados basándose en entradas
- Validar la funcionalidad del diseño
- Identificar patrones y anomalías

## 🏗️ Arquitectura del Proyecto

```
ml_random_forest/
├── mult.sv                    # RTL del multiplicador de 8 bits
├── test_mult_rf.py           # Testbench con Random Forest
├── Makefile                  # Configuración de cocotb
└── README.md                 # Este archivo
```

## 🔧 Componentes

### 1. Multiplicador (mult.sv)
- **Entradas**: `a[7:0]`, `b[7:0]`
- **Salida**: `product[15:0]`
- Multiplicador combinacional simple
- Rango: 0-255 × 0-255 = 0-65025

### 2. Random Forest Verifier (test_mult_rf.py)

El verificador basado en Random Forest implementa tres fases:

#### **Fase 1: Entrenamiento**
- Recolecta 500 muestras de entrenamiento
- Genera entradas aleatorias
- Calcula productos esperados (golden reference)
- Entrena el modelo Random Forest con estos datos
- Reporta métricas: MSE, R² score, feature importance

#### **Fase 2: Verificación ML**
- Usa el modelo entrenado para predecir resultados
- Compara predicciones ML vs resultados reales
- Compara salidas DUT vs resultados esperados
- Genera estadísticas de precisión

#### **Fase 3: Análisis y Visualización**
- Calcula métricas de rendimiento
- Genera gráficas de predicciones
- Reporta precisión del DUT y del modelo ML

### 3. Tests Adicionales

- **test_edge_cases**: Verifica casos límite (0×0, 255×255, etc.)
- **test_exhaustive_small**: Test exhaustivo para valores 0-15

## 🤖 Random Forest: ¿Por qué?

### Ventajas del Random Forest en Verificación:

1. **Robustez**: Menos propenso al overfitting que modelos individuales
2. **Feature Importance**: Identifica qué entradas son más importantes
3. **No requiere normalización**: Trabaja bien con datos sin preprocesar
4. **Interpretabilidad**: Los árboles pueden ser visualizados
5. **Maneja relaciones no lineales**: Captura interacciones complejas

### Hiperparámetros Utilizados:

```python
RandomForestRegressor(
    n_estimators=100,      # 100 árboles en el bosque
    max_depth=20,          # Profundidad máxima de 20 niveles
    random_state=42,       # Reproducibilidad
    n_jobs=-1              # Usa todos los núcleos del CPU
)
```

## 📊 Métricas de Evaluación

El sistema reporta las siguientes métricas:

1. **MSE (Mean Squared Error)**: Error cuadrático medio de las predicciones
2. **R² Score**: Coeficiente de determinación (1.0 = predicción perfecta)
3. **Accuracy**: Porcentaje de predicciones exactas
4. **Feature Importance**: Importancia relativa de cada entrada

## 🚀 Uso

### Requisitos Previos

```bash
pip install cocotb scikit-learn numpy matplotlib
```

### Ejecutar Todos los Tests

```bash
cd ml_random_forest
make
```

### Ejecutar Tests Específicos

```bash
# Solo test de Random Forest
make test_rf

# Solo casos límite
make test_edge

# Test exhaustivo
make test_exhaustive
```

### Limpiar Archivos Generados

```bash
make clean
```

## 📈 Resultados Esperados

### Salida del Test:

```
[PHASE 1] Training the Random Forest Model
Collected 500/500 training samples
Model training complete!
  - Training samples: 400
  - Test samples: 100
  - Mean Squared Error: 0.0000
  - R² Score: 1.0000

Feature Importance:
  - Input A: 0.5000
  - Input B: 0.5000

[PHASE 2] ML-Driven Verification
Verified 200/200 test cases

[PHASE 3] Verification Results
Test Summary:
  - Total test cases: 200
  - ML Prediction accuracy: 100.00% (200/200)
  - DUT accuracy: 100.00% (200/200)

✓ VERIFICATION PASSED: DUT is functioning correctly!
✓ ML MODEL EXCELLENT: 100.00% accuracy achieved!
```

### Visualización:

Se genera `rf_verification_results.png` con:
- **Gráfica 1**: Predicciones ML vs Valores Reales
- **Gráfica 2**: Distribución de Errores de Predicción

## 🔍 Análisis de Feature Importance

Para un multiplicador ideal, se espera:
- **Input A**: ~50% de importancia
- **Input B**: ~50% de importancia

Esto confirma que ambas entradas contribuyen igualmente al resultado, lo cual tiene sentido matemáticamente.

## 🧪 Cobertura de Tests

1. **Random Testing**: 500 casos de entrenamiento + 200 de verificación
2. **Edge Cases**: 8 casos límite críticos
3. **Exhaustive**: 256 casos (16×16) para valores pequeños

Total: **~764 casos de prueba**

## 💡 Extensiones Posibles

1. **Comparar con otros modelos**: Decision Trees, Gradient Boosting, Neural Networks
2. **Optimización de hiperparámetros**: Grid Search o Random Search
3. **Detección de anomalías**: Identificar comportamientos inesperados
4. **Cobertura dirigida**: Usar el modelo para generar casos de prueba interesantes
5. **Análisis de SHAP values**: Explicabilidad mejorada

## 📚 Conceptos Clave

### Random Forest
Un conjunto (ensemble) de árboles de decisión que:
- Cada árbol se entrena con una muestra bootstrap de los datos
- Cada división considera un subconjunto aleatorio de features
- La predicción final es el promedio de todos los árboles
- Reduce varianza y mejora generalización

### Ventajas en Verificación
- **Aprendizaje del comportamiento**: El modelo aprende patrones complejos
- **Detección de inconsistencias**: Desvíos de las predicciones indican errores
- **Eficiencia**: Después del entrenamiento, las predicciones son rápidas
- **Paralelización**: Árboles pueden evaluarse en paralelo

## 🎓 Referencias

- scikit-learn RandomForestRegressor: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
- Cocotb Documentation: https://docs.cocotb.org/
- Random Forests (Breiman, 2001): Paper original sobre Random Forests

## 📝 Notas

- El modelo Random Forest es particularmente efectivo para este caso porque la función de multiplicación es determinística y bien definida
- Con suficientes datos de entrenamiento, el modelo debería alcanzar 100% de precisión
- La visualización ayuda a identificar cualquier sesgo o patrón de error
- Feature importance confirma que ambas entradas son igualmente relevantes

---

**Autor**: Proyecto de Verificación con ML  
**Fecha**: Febrero 2026  
**Herramientas**: Cocotb + scikit-learn + Icarus Verilog
