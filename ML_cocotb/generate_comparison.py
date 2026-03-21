#!/usr/bin/env python3
"""
Generador de Gráfico Comparativo: Random vs ML-Temporal

Crea visualizaciones comparativas basadas en los resultados experimentales.
"""

import matplotlib.pyplot as plt
import numpy as np

# Datos experimentales obtenidos de las ejecuciones
random_results = {
    'first_overflow': 3,
    'total_overflows': 73,
    'max_magnitude': 29760,
    'overflow_rate': 12.17,
    'total_cycles': 600,
    'execution_time': 0.71
}

ml_temporal_results = {
    'first_overflow': 4,
    'total_overflows': 475,
    'max_magnitude': 30720,
    'overflow_rate': 79.17,
    'total_cycles': 600,
    'execution_time': 1.71
}

def create_comparison_chart():
    """
    Crea gráfico de barras comparativo.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    methods = ['Random', 'ML-Temporal']
    colors = ['#e74c3c', '#2ecc71']
    
    # 1. Convergencia (Primer Overflow)
    ax1 = axes[0, 0]
    first_of = [random_results['first_overflow'], ml_temporal_results['first_overflow']]
    bars1 = ax1.bar(methods, first_of, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Ciclos', fontsize=12, fontweight='bold')
    ax1.set_title('Primer Overflow Detectado\n(Menor es Mejor)', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, max(first_of) * 1.5)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, value in zip(bars1, first_of):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(value)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 2. Total de Overflows
    ax2 = axes[0, 1]
    total_of = [random_results['total_overflows'], ml_temporal_results['total_overflows']]
    bars2 = ax2.bar(methods, total_of, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Cantidad de Overflows', fontsize=12, fontweight='bold')
    ax2.set_title('Cobertura de Corner Cases\n(Mayor es Mejor)', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, max(total_of) * 1.2)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, value in zip(bars2, total_of):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(value)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Añadir factor de mejora
    improvement = ml_temporal_results['total_overflows'] / random_results['total_overflows']
    ax2.text(0.5, max(total_of) * 0.95, f'Mejora: {improvement:.1f}x',
            ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # 3. Magnitud Máxima
    ax3 = axes[1, 0]
    max_mag = [random_results['max_magnitude'], ml_temporal_results['max_magnitude']]
    bars3 = ax3.bar(methods, max_mag, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax3.set_ylabel('Magnitud Absoluta', fontsize=12, fontweight='bold')
    ax3.set_title('Máximo Alcanzado\n(Mayor es Mejor)', fontsize=13, fontweight='bold')
    ax3.axhline(y=16000, color='orange', linestyle='--', linewidth=2, label='Umbral Overflow')
    ax3.axhline(y=30720, color='red', linestyle=':', linewidth=2, label='Máximo Teórico')
    ax3.set_ylim(0, 35000)
    ax3.legend(loc='upper left', fontsize=9)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, value in zip(bars3, max_mag):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(value):,}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 4. Tasa de Overflow
    ax4 = axes[1, 1]
    of_rate = [random_results['overflow_rate'], ml_temporal_results['overflow_rate']]
    bars4 = ax4.bar(methods, of_rate, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax4.set_ylabel('Porcentaje (%)', fontsize=12, fontweight='bold')
    ax4.set_title('Eficiencia de Detección\n(Mayor es Mejor)', fontsize=13, fontweight='bold')
    ax4.set_ylim(0, 100)
    ax4.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, value in zip(bars4, of_rate):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Factor de mejora
    improvement_rate = ml_temporal_results['overflow_rate'] / random_results['overflow_rate']
    ax4.text(0.5, 90, f'Mejora: {improvement_rate:.1f}x',
            ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    plt.suptitle('Comparación: Verificación Random vs ML-Temporal\nFiltro FIR - Coeficientes [80, 80, 80] - 600 Ciclos',
                fontsize=15, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    
    output_file = "final_comparison_chart.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Gráfico comparativo guardado: {output_file}")
    
    return output_file


def create_summary_table():
    """
    Crea tabla visual de resumen.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    
    headers = ['Métrica', 'Random', 'ML-Temporal', 'Mejora']
    
    table_data = [
        ['Primer Overflow (ciclos)', 
         str(random_results['first_overflow']),
         str(ml_temporal_results['first_overflow']),
         'Similar'],
        
        ['Total Overflows', 
         str(random_results['total_overflows']),
         str(ml_temporal_results['total_overflows']),
         f"{ml_temporal_results['total_overflows']/random_results['total_overflows']:.1f}x"],
        
        ['Tasa de Overflow (%)', 
         f"{random_results['overflow_rate']:.1f}%",
         f"{ml_temporal_results['overflow_rate']:.1f}%",
         f"{ml_temporal_results['overflow_rate']/random_results['overflow_rate']:.1f}x"],
        
        ['Magnitud Máxima', 
         f"{random_results['max_magnitude']:,}",
         f"{ml_temporal_results['max_magnitude']:,}",
         f"+{ml_temporal_results['max_magnitude']-random_results['max_magnitude']}"],
        
        ['Tiempo Ejecución (s)', 
         f"{random_results['execution_time']:.2f}",
         f"{ml_temporal_results['execution_time']:.2f}",
         f"{ml_temporal_results['execution_time']/random_results['execution_time']:.1f}x más lento"],
    ]
    
    table = ax.table(cellText=table_data, colLabels=headers,
                    cellLoc='center', loc='center',
                    colWidths=[0.35, 0.2, 0.2, 0.25])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Estilo de header
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Estilo de filas
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#ecf0f1')
            else:
                table[(i, j)].set_facecolor('#ffffff')
            
            # Resaltar mejoras en verde
            if j == 3 and 'x' in str(table_data[i-1][j]) and 'más lento' not in str(table_data[i-1][j]):
                table[(i, j)].set_facecolor('#d5f4e6')
                table[(i, j)].set_text_props(weight='bold', color='#27ae60')
    
    plt.title('Tabla Resumen de Comparación\nRandom vs ML-Temporal', 
             fontsize=14, fontweight='bold', pad=20)
    
    output_file = "comparison_summary_table.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Tabla resumen guardada: {output_file}")
    
    return output_file


def print_text_summary():
    """
    Imprime resumen textual en consola.
    """
    print("\n" + "="*80)
    print(" "*20 + "RESUMEN DE COMPARACIÓN EXPERIMENTAL")
    print("="*80)
    
    print(f"\n{'Métrica':<30} {'Random':<15} {'ML-Temporal':<15} {'Mejora':<15}")
    print("-" * 80)
    
    print(f"{'Primer Overflow (ciclos)':<30} {random_results['first_overflow']:<15} {ml_temporal_results['first_overflow']:<15} {'Similar':<15}")
    
    overflow_improvement = ml_temporal_results['total_overflows'] / random_results['total_overflows']
    print(f"{'Total Overflows':<30} {random_results['total_overflows']:<15} {ml_temporal_results['total_overflows']:<15} {overflow_improvement:.1f}x")
    
    rate_improvement = ml_temporal_results['overflow_rate'] / random_results['overflow_rate']
    print(f"{'Tasa Overflow (%)':<30} {random_results['overflow_rate']:<15.1f} {ml_temporal_results['overflow_rate']:<15.1f} {rate_improvement:.1f}x")
    
    mag_diff = ml_temporal_results['max_magnitude'] - random_results['max_magnitude']
    print(f"{'Magnitud Máxima':<30} {random_results['max_magnitude']:<15,} {ml_temporal_results['max_magnitude']:<15,} {'+' + str(mag_diff):<15}")
    
    time_ratio = ml_temporal_results['execution_time'] / random_results['execution_time']
    print(f"{'Tiempo Ejecución (s)':<30} {random_results['execution_time']:<15.2f} {ml_temporal_results['execution_time']:<15.2f} {time_ratio:.1f}x")
    
    print("\n" + "="*80)
    print("\n🎯 CONCLUSIONES CLAVE:")
    print(f"   ✓ ML-Temporal detectó {overflow_improvement:.1f}x MÁS overflows")
    print(f"   ✓ ML-Temporal alcanzó el MÁXIMO TEÓRICO ({ml_temporal_results['max_magnitude']:,})")
    print(f"   ✓ ML-Temporal logró {ml_temporal_results['overflow_rate']:.1f}% de tasa de éxito")
    print(f"   ✓ Random solo logró {random_results['overflow_rate']:.1f}% de tasa de éxito")
    print(f"   ⚠ ML-Temporal es {time_ratio:.1f}x más lento (trade-off aceptable)")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  Generador de Visualizaciones Comparativas                     ║
    ║  Random Verification vs ML-Guided Temporal                     ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    print_text_summary()
    
    print("Generando visualizaciones...\n")
    
    try:
        create_comparison_chart()
        create_summary_table()
        
        print("\n✓ Todas las visualizaciones generadas exitosamente")
        print("\nArchivos creados:")
        print("  - final_comparison_chart.png")
        print("  - comparison_summary_table.png")
        print("\nConsulte RESULTS_COMPARISON.md para análisis detallado.")
        
    except Exception as e:
        print(f"\n✗ Error generando visualizaciones: {e}")
        import traceback
        traceback.print_exc()
