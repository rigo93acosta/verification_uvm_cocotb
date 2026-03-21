#!/bin/bash
# Script para ejecutar todos los métodos de verificación y compararlos

echo "=========================================================================="
echo "  Ejecutando Comparación de Métodos de Verificación"
echo "=========================================================================="
echo ""

# Crear directorio para resultados si no existe
mkdir -p comparison_results

# Función para ejecutar y guardar logs
run_test() {
    local module=$1
    local name=$2
    local output_file="comparison_results/${name}_output.log"
    
    echo "----------------------------------------------------------------------"
    echo "Ejecutando: $name"
    echo "Módulo: $module"
    echo "----------------------------------------------------------------------"
    
    make clean > /dev/null 2>&1
    make SIM=icarus TOPLEVEL=filter MODULE=$module 2>&1 | tee "$output_file"
    
    if [ $? -eq 0 ]; then
        echo "✓ $name completado exitosamente"
    else
        echo "✗ $name falló"
    fi
    
    echo ""
}

# Ejecutar todos los testbenches
echo "1/4: Método Aleatorio (Baseline)..."
run_test "test_fir_random" "random"

echo "2/4: Método ML Clasificador..."
run_test "test_fir_ml" "ml_classifier"

echo "3/4: Método ML Regresor..."
run_test "test_fir_ml_regressor" "ml_regressor"

echo "4/4: Método ML Temporal (Con Memoria)..."
run_test "test_fir_ml_memory" "ml_temporal"

echo "=========================================================================="
echo "  Ejecución Completada"
echo "=========================================================================="
echo ""
echo "Resultados guardados en: comparison_results/"
echo ""
echo "Archivos generados:"
ls -lh *.png 2>/dev/null | awk '{print "  - " $9}'
echo ""

# Extraer métricas clave
echo "=========================================================================="
echo "  RESUMEN DE MÉTRICAS"
echo "=========================================================================="
echo ""

extract_metrics() {
    local file=$1
    local name=$2
    
    echo "[$name]"
    
    # Buscar primer overflow
    first_of=$(grep -o "Primer Overflow en Ciclo:\s*[0-9]*" "$file" | grep -o "[0-9]*$" | head -1)
    if [ -z "$first_of" ]; then
        first_of=$(grep -o "PRIMER OVERFLOW detectado en ciclo [0-9]*" "$file" | grep -o "[0-9]*" | head -1)
    fi
    
    # Buscar total overflows
    total_of=$(grep -o "Total.*Overflows.*:\s*[0-9]*" "$file" | grep -o "[0-9]*$" | head -1)
    
    # Buscar magnitud máxima
    max_mag=$(grep -o "Magnitud Máxima.*:\s*[0-9]*" "$file" | grep -o "[0-9]*$" | head -1)
    
    echo "  Primer Overflow:    ${first_of:-N/A}"
    echo "  Total Overflows:    ${total_of:-N/A}"
    echo "  Magnitud Máxima:    ${max_mag:-N/A}"
    echo ""
}

extract_metrics "comparison_results/random_output.log" "Random (Baseline)"
extract_metrics "comparison_results/ml_classifier_output.log" "ML Clasificador"
extract_metrics "comparison_results/ml_regressor_output.log" "ML Regresor"
extract_metrics "comparison_results/ml_temporal_output.log" "ML Temporal"

echo "=========================================================================="
echo "Para análisis detallado con gráficos, ejecute:"
echo "  python3 compare_verification_methods.py"
echo "=========================================================================="
