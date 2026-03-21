# Índice de Archivos del Proyecto

## 📁 Estructura del Proyecto

```
ML_cocotb/
├── Core HDL
│   └── filter.v                          # Filtro FIR de orden 2 (DUT)
│
├── Agentes ML
│   ├── ml_agent.py                       # Clasificador ML (binario)
│   ├── ml_agent_regressor.py             # Regresor ML (magnitud)
│   └── ml_temporal_agent.py              # Regresor con memoria temporal ⭐
│
├── Testbenches
│   ├── test_fir_random.py                # Verificación aleatoria (baseline) ⭐
│   ├── test_fir_ml.py                    # Testbench con clasificador
│   ├── test_fir_ml_regressor.py          # Testbench con regresor
│   └── test_fir_ml_memory.py             # Testbench con agente temporal ⭐
│
├── Scripts de Análisis
│   ├── generate_comparison.py            # Generador de visualizaciones ⭐
│   ├── compare_verification_methods.py   # Comparador automático completo
│   └── run_comparison.sh                 # Script de ejecución batch
│
├── Visualizaciones
│   ├── final_comparison_chart.png        # Comparación Random vs ML ⭐
│   ├── comparison_summary_table.png      # Tabla de métricas ⭐
│   ├── random_verification_curve.png     # Curva método aleatorio ⭐
│   ├── ml_learning_curve.png             # Curva ML temporal ⭐
│   └── verification_progress.png         # Curva ML regresor básico
│
├── Documentación
│   ├── README.md                         # Documentación técnica completa
│   ├── EXECUTIVE_SUMMARY.md              # Resumen ejecutivo ⭐
│   ├── RESULTS_COMPARISON.md             # Análisis de resultados ⭐
│   ├── COMPARISON.md                     # Guía de comparación
│   └── INDEX.md                          # Este archivo
│
└── Configuración
    ├── Makefile                          # Configuración de cocotb
    └── results.xml                       # Resultados de última ejecución
```

⭐ = Archivos clave para la comparación

---

## 📄 Descripción Detallada

### Core HDL

**filter.v**
- Filtro FIR de segundo orden
- 3 coeficientes configurables
- Detección de overflow incorporada
- Salida de 16 bits con signo

### Agentes ML

**ml_agent.py**
- Clasificación binaria (overflow/no overflow)
- Random Forest Classifier
- Problema: Genera warnings (mal formulado)

**ml_agent_regressor.py**
- Predicción de magnitud
- Random Forest Regressor
- Epsilon-greedy (90% explotación, 10% exploración)

**ml_temporal_agent.py** ⭐
- Predicción con contexto temporal
- Sliding window de profundidad 3
- Aprende secuencias óptimas
- Mejor rendimiento de todos los métodos

### Testbenches

**test_fir_random.py** ⭐
- Estimulación completamente aleatoria
- Baseline para comparación
- 600 iteraciones
- Genera: random_verification_curve.png

**test_fir_ml.py**
- Usa ml_agent.py (clasificador)
- 200 iteraciones
- Experimental

**test_fir_ml_regressor.py**
- Usa ml_agent_regressor.py
- 300 iteraciones
- Genera: verification_progress.png

**test_fir_ml_memory.py** ⭐
- Usa ml_temporal_agent.py
- 600 iteraciones
- Genera: ml_learning_curve.png
- Mejor método ML

### Scripts de Análisis

**generate_comparison.py** ⭐
- Crea visualizaciones comparativas
- Basado en datos experimentales reales
- Genera:
  - final_comparison_chart.png
  - comparison_summary_table.png
- Uso: `python3 generate_comparison.py`

**compare_verification_methods.py**
- Ejecuta todos los testbenches automáticamente
- Parsea resultados
- Genera comparación completa
- Uso interactivo

**run_comparison.sh**
- Script bash para ejecución batch
- Guarda logs en comparison_results/
- Extrae métricas automáticamente
- Uso: `./run_comparison.sh`

### Visualizaciones

**final_comparison_chart.png** ⭐
- 4 gráficos de barras comparativos:
  1. Convergencia (primer overflow)
  2. Cobertura (total overflows)
  3. Magnitud máxima
  4. Eficiencia (tasa de overflow)
- Muestra mejora de 6.5x de ML vs Random

**comparison_summary_table.png** ⭐
- Tabla visual de todas las métricas
- Incluye factores de mejora
- Resalta beneficios del ML

**random_verification_curve.png** ⭐
- Curva de magnitudes del método aleatorio
- Patrón errático
- Media móvil plana
- Tasa de overflow: 12.2%

**ml_learning_curve.png** ⭐
- Curva de magnitudes del ML temporal
- Tendencia ascendente clara
- Convergencia al máximo teórico
- Tasa de overflow: 79.2%

**verification_progress.png**
- Curva del ML regresor básico (sin memoria)
- Método intermedio

### Documentación

**README.md**
- Documentación técnica completa
- Teoría de ML aplicada
- Arquitectura del sistema
- Fundamentos matemáticos
- ~500 líneas de documentación detallada

**EXECUTIVE_SUMMARY.md** ⭐
- Resumen de 1 página
- Resultados principales
- Conclusiones clave
- Para audiencia ejecutiva/gerencial

**RESULTS_COMPARISON.md** ⭐
- Análisis detallado de resultados experimentales
- Comparación Random vs ML-Temporal
- Interpretación de gráficos
- Descubrimientos del modelo

**COMPARISON.md**
- Guía de ejecución paso a paso
- Opciones de comparación
- Interpretación de métricas
- Comandos de ejecución

**INDEX.md** (este archivo)
- Índice completo del proyecto
- Descripción de cada archivo
- Roadmap de navegación

---

## 🎯 Guía de Lectura Recomendada

### Para Comenzar Rápido
1. **EXECUTIVE_SUMMARY.md** - Resultados en 2 minutos
2. **final_comparison_chart.png** - Visualización clave
3. **RESULTS_COMPARISON.md** - Análisis completo

### Para Entender el Proyecto
1. **README.md** Sección 1 (Introducción)
2. **README.md** Sección 2 (Arquitectura)
3. **COMPARISON.md** - Cómo ejecutar

### Para Implementar/Modificar
1. **README.md** completo
2. **ml_temporal_agent.py** - Código del mejor agente
3. **test_fir_ml_memory.py** - Testbench correspondiente

### Para Verificar Resultados
1. Ejecutar: `make MODULE=test_fir_random`
2. Ejecutar: `make MODULE=test_fir_ml_memory`
3. Ejecutar: `python3 generate_comparison.py`
4. Revisar: **RESULTS_COMPARISON.md**

---

## 📊 Resultados Clave (Referencia Rápida)

| Métrica | Random | ML-Temporal | Mejora |
|---------|--------|-------------|--------|
| Cobertura | 73 OF | **475 OF** | **6.5x** |
| Eficiencia | 12.2% | **79.2%** | **6.5x** |
| Máximo | 29,760 | **30,720** | **+3.2%** |

---

## 🔄 Comandos Rápidos

```bash
# Ejecutar comparación completa
./run_comparison.sh

# Solo random
make MODULE=test_fir_random

# Solo ML temporal
make MODULE=test_fir_ml_memory

# Generar visualizaciones
python3 generate_comparison.py

# Limpiar
make clean
rm -f *.png comparison_results/*
```

---

**Última actualización**: 1 Febrero 2026  
**Versión**: 1.0  
**Autor**: Rigoberto Acosta González
