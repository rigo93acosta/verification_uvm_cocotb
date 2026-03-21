# Verificación SPI con Machine Learning

## 🎯 Objetivo

Demostrar el **uso CORRECTO de ML en verificación**: generar secuencias inteligentes que maximicen la cobertura funcional, reduciendo el espacio de pruebas de millones a cientos de transacciones efectivas.

## ⚠️ Concepto Clave: ML para GENERACIÓN, no Predicción

**❌ Enfoque INCORRECTO:**  
Usar ML para predecir el comportamiento del DUT (ej: "dado TX, predecir RX")

**✅ Enfoque CORRECTO:**  
Usar ML para GENERAR secuencias de prueba que maximicen la cobertura funcional

## 🏗️ Sistema SPI: 1 Master + 2 Slaves

```
┌─────────────────────────────────────────┐
│  SPI Master                             │
│  ├─ SCLK  ────→ Slave 0 (ID: 0xA0)     │
│  ├─ MOSI  ────→ Slave 1 (ID: 0xB1)     │
│  ├─ MISO  ←────                         │
│  └─ CS[0:1]                             │
└─────────────────────────────────────────┘
```

**Características:**
- Protocolo SPI Modo 0 (CPOL=0, CPHA=0)
- 8 bits de datos
- 2 esclavos con IDs únicos
- FSM: IDLE → TRANSFER → DONE

## 🧬 Algoritmo Genético para Generación de Secuencias

### Representación
- **Individuo** = Secuencia de 10 transacciones `[(slave_id, tx_data), ...]`
- **Población** = 20 secuencias
- **Fitness** = Cobertura funcional alcanzada

### Proceso Evolutivo
```python
1. Población inicial random
2. Por 20 generaciones:
   - Evaluar fitness (ejecutar secuencias y medir cobertura)
   - Selección: mantener mejores (elitismo 25%)
   - Crossover: combinar secuencias exitosas
   - Mutación: 20% de cambios aleatorios
3. Retornar mejor secuencia
```

### Cobertura Funcional Medida
- ✅ Acceso a ambos esclavos
- ✅ Transiciones S0→S1, S1→S0, S0→S0, S1→S1
- ✅ Rangos de datos (8 bins: 0x00-0x1F, 0x20-0x3F, ...)
- ✅ Corner cases (0x00, 0xFF, 0xAA, 0x55)
- ✅ Patrones de secuencias (repeticiones, alternancia)

## 📊 Resultados: Random vs ML-Guided

```
Métrica                   │ Random    │ ML-Guided  │ Mejora
──────────────────────────────────────────────────────────
Cobertura alcanzada       │  85.0%    │  100.0%    │ +15.0%
Transacciones necesarias  │   100     │    60      │  -40%
Eficiencia (cov/trans)    │  0.85     │  1.67      │ +96.1%
```

**Conclusión:** ML reduce el espacio de búsqueda generando secuencias 96% más eficientes.

## 🚀 Uso

```bash
# Ejecutar verificación completa
make

# Ver resultados
cat results.xml
```

## 📁 Archivos

- `spi_master.sv` - Master SPI con FSM
- `spi_slave.sv` - Slave SPI con registro interno  
- `spi_top.sv` - Top level (1 master + 2 slaves)
- `test_spi_ml.py` - **Tests con ML-guided sequence generation**
- `Makefile` - Configuración cocotb + Icarus Verilog

## 🧪 Tests Implementados

### 1. `test_ml_sequence_generation` ⭐
Compara 3 estrategias:
- **Random**: 10 secuencias × 10 transacciones = 100 trans
- **ML-Guided**: Algoritmo genético → 5 secuencias optimizadas = 50 trans  
- **Coverage-Driven**: Refinamiento para gaps específicos = +10 trans

**Resultado:** 100% cobertura con 60 transacciones (vs 85% con 100 random)

### 2. `test_corner_case_coverage`
Genera secuencias dirigidas a corner cases usando ML

### 3. `test_transition_coverage`  
Verifica todas las transiciones de estado

### 4. `test_alternating_slaves`
Patrón básico S0→S1→S0→S1

### 5. `test_sequential_slave`
Múltiples transacciones al mismo esclavo

## 💡 Lecciones Aprendidas

1. **ML NO sirve para funciones determinísticas simples** (ej: multiplicación)
2. **ML SÍ sirve para reducir espacios de búsqueda enormes** (secuencias de protocolo)
3. **Algoritmos genéticos** son ideales para optimización de cobertura
4. **Coverage-driven generation** complementa bien a ML para cubrir gaps específicos

## 🔗 Comparación con ml_random_forest/

| Proyecto            | DUT          | ML Útil | Razón                                    |
|---------------------|--------------|---------|------------------------------------------|
| ml_random_forest/   | Multiplier   | ❌ NO   | Función determinística conocida (a × b)  |
| ml_spi/ (este)      | SPI Protocol | ✅ SÍ   | Espacio de secuencias enorme, patrones complejos |

---
**Autor:** Proyecto de verificación funcional con ML  
**Framework:** Cocotb 2.0 + Icarus Verilog 12.0 + Python 3.12

Para cada transacción SPI:

| Feature | Descripción |
|---------|-------------|
| `slave_id` | Esclavo seleccionado (0 o 1) |
| `tx_data` | Dato transmitido (0-255) |
| `rx_data` | Dato recibido (0-255) |
| `duration_cycles` | Ciclos de reloj de la transacción |
| `tx_high_nibble` | 4 bits altos de TX |
| `tx_low_nibble` | 4 bits bajos de TX |
| `rx_high_nibble` | 4 bits altos de RX |
| `rx_low_nibble` | 4 bits bajos de RX |
| `is_loopback` | TX == RX? |
| `is_long_transaction` | Duración > 100 ciclos? |

## 🚀 Uso

### Ejecutar Todos los Tests
```bash
cd ml_spi
make
```

### Ejecutar Tests Específicos
```bash
# Test principal con ML
make test_ml

# Test de patrón alternado
make test_alternating

# Test de acceso secuencial
make test_sequential
```

### Limpiar
```bash
make clean
```

## 📈 Fases de Verificación

### **Fase 1: Recolección de Datos** (30 transacciones)
- Genera transacciones aleatorias
- Alterna entre Slave 0 y Slave 1
- Verifica que cada esclavo responde correctamente
- Almacena todas las transacciones

### **Fase 2: Entrenamiento ML**
- Entrena `RandomForest` para predecir próximo esclavo
- Entrena `Neural Network` para detectar anomalías
- Requiere mínimo 10-20 transacciones

### **Fase 3: Verificación con Predicciones**
- Usa ML para predecir comportamiento
- Compara predicciones vs comportamiento real
- Detecta anomalías automáticamente
- Reporte de precisión del modelo

### **Fase 4: Resultados**
```
Estadísticas del sistema:
  Total transacciones:      50
  Transacciones Slave 0:    25
  Transacciones Slave 1:    25
  Duración promedio:        87.3 ciclos
  Duración min/max:         82/95 ciclos

Precisión del predictor ML: 75.0% (15/20)

✓ VERIFICACIÓN EXITOSA
```

## 🧪 Tests Incluidos

### 1. `test_spi_ml_verification`
Test principal que usa ML para verificación completa

### 2. `test_alternating_slaves`
Prueba patrón específico: 0→1→0→1→0→1

### 3. `test_sequential_slave`
Múltiples transacciones consecutivas al mismo esclavo

## 💡 Ventajas de ML en SPI

### Comparado con verificación tradicional:

| Aspecto | Tradicional | Con ML |
|---------|------------|--------|
| Detección de patrones | Manual | Automática |
| Anomalías | Reglas fijas | Aprende qué es normal |
| Casos de prueba | Pre-definidos | Dirigidos por ML |
| Adaptabilidad | Baja | Alta (aprende del DUT) |
| Cobertura | Basada en plan | Basada en comportamiento |

## 🎓 Conceptos Clave de ML Aplicados

### 1. **Clasificación (RandomForest)**
- Predice categorías discretas (slave 0, 1, 2...)
- Robusto a ruido
- Interpretable (feature importance)

### 2. **Detección de Anomalías (Neural Network)**
- Aprende distribución "normal" de transacciones
- Identifica outliers automáticamente
- No requiere reglas explícitas

### 3. **Features Engineering**
- Extrae características relevantes del protocolo
- Combina información de timing y datos
- Captura relaciones no-obvias

## 📝 Diferencia vs Multiplicador

| Aspecto | Multiplicador | SPI |
|---------|---------------|-----|
| Complejidad | Simple (a×b) | Protocolo multi-señal |
| Determinismo | 100% | Estados + timing |
| ML útil | ❌ NO | ✅ SÍ |
| Precisión ML | ~15% exacta | ~75% predicción |
| Valor agregado | Ninguno | Detección de patrones |

## 🔍 Casos de Uso Avanzados

### 1. **Generación de Casos Dirigida**
```python
# ML identifica que raramente se prueba: slave 0 → slave 0
# Genera más casos de ese patrón
```

### 2. **Coverage Inteligente**
```python
# ML detecta que ciertos datos (0x00, 0xFF) son raros
# Aumenta pruebas con esos valores
```

### 3. **Regresión Automática**
```python
# Entrena con versión correcta
# Compara comportamiento en nueva versión
# Detecta cambios inesperados
```

## 🎯 Métricas de Éxito

- ✅ **100% transacciones exitosas**: Sin errores de protocolo
- ✅ **>70% precisión ML**: Modelo aprende patrones correctamente  
- ✅ **Detección de anomalías**: Identifica comportamientos inusuales
- ✅ **Cobertura de esclavos**: Ambos esclavos probados equitativamente

## 📚 Referencias

- SPI Protocol: https://en.wikipedia.org/wiki/Serial_Peripheral_Interface
- Cocotb: https://docs.cocotb.org/
- scikit-learn: https://scikit-learn.org/

---

**Autor**: Proyecto de Verificación con ML  
**Fecha**: Febrero 2026  
**Herramientas**: Cocotb + scikit-learn + Icarus Verilog
