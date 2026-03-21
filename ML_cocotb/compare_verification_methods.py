#!/usr/bin/env python3
"""
Script de Comparación de Métodos de Verificación
=================================================

Este script ejecuta todos los testbenches (Random, ML Clasificador, ML Regresor, ML Temporal)
y genera un análisis comparativo completo con visualizaciones.

Uso:
    python3 compare_verification_methods.py

Nota: Requiere haber ejecutado previamente todos los testbenches individualmente
      para tener los archivos de resultados.
"""

import subprocess
import re
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import time

class VerificationComparator:
    """
    Clase para ejecutar y comparar diferentes métodos de verificación.
    """
    
    def __init__(self):
        self.results = {}
        self.makefile_path = Path("Makefile")
        
    def run_testbench(self, module_name, method_name):
        """
        Ejecuta un testbench específico y extrae métricas.
        
        Args:
            module_name: Nombre del módulo Python (ej: test_fir_random)
            method_name: Nombre descriptivo (ej: "Random")
        """
        print(f"\n{'='*70}")
        print(f"Ejecutando: {method_name}")
        print(f"Módulo: {module_name}")
        print(f"{'='*70}\n")
        
        # Ejecutar make con el módulo específico
        cmd = f"make SIM=icarus TOPLEVEL=filter MODULE={module_name}"
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            execution_time = time.time() - start_time
            
            # Parsear resultados del output
            metrics = self.parse_output(result.stdout, result.stderr)
            metrics['execution_time'] = execution_time
            metrics['success'] = result.returncode == 0
            
            self.results[method_name] = metrics
            
            print(f"\n✓ {method_name} completado en {execution_time:.2f}s")
            print(f"  Overflows: {metrics.get('overflow_count', 'N/A')}")
            print(f"  Primer overflow: Ciclo {metrics.get('first_overflow_cycle', 'N/A')}")
            print(f"  Mag. máxima: {metrics.get('max_magnitude', 'N/A')}")
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"✗ {method_name} excedió tiempo límite")
            self.results[method_name] = {'success': False, 'error': 'Timeout'}
            return False
            
        except Exception as e:
            print(f"✗ Error ejecutando {method_name}: {e}")
            self.results[method_name] = {'success': False, 'error': str(e)}
            return False
    
    def parse_output(self, stdout, stderr):
        """
        Extrae métricas del output de cocotb.
        """
        metrics = {
            'overflow_count': 0,
            'first_overflow_cycle': None,
            'max_magnitude': 0,
            'overflow_rate': 0.0
        }
        
        combined_output = stdout + stderr
        
        # Buscar total de overflows
        overflow_match = re.search(r'Total de Overflows:\s*(\d+)', combined_output)
        if overflow_match:
            metrics['overflow_count'] = int(overflow_match.group(1))
        else:
            # Alternativa: Total Overflows encontrados
            overflow_match = re.search(r'Total Overflows encontrados:\s*(\d+)', combined_output)
            if overflow_match:
                metrics['overflow_count'] = int(overflow_match.group(1))
        
        # Buscar primer overflow
        first_overflow_match = re.search(r'Primer Overflow en Ciclo:\s*(\d+)', combined_output)
        if first_overflow_match:
            metrics['first_overflow_cycle'] = int(first_overflow_match.group(1))
        else:
            # Alternativa: PRIMER OVERFLOW detectado en ciclo
            first_overflow_match = re.search(r'PRIMER OVERFLOW detectado en ciclo (\d+)', combined_output)
            if first_overflow_match:
                metrics['first_overflow_cycle'] = int(first_overflow_match.group(1))
        
        # Buscar magnitud máxima
        max_mag_match = re.search(r'Magnitud Máxima [Aa]lcanzada:\s*(\d+)', combined_output)
        if max_mag_match:
            metrics['max_magnitude'] = int(max_mag_match.group(1))
        
        # Buscar tasa de overflow
        rate_match = re.search(r'Tasa de Overflow:\s*([\d.]+)%', combined_output)
        if rate_match:
            metrics['overflow_rate'] = float(rate_match.group(1))
        
        return metrics
    
    def generate_comparison_report(self):
        """
        Genera reporte textual comparativo.
        """
        print("\n" + "="*70)
        print("REPORTE COMPARATIVO DE MÉTODOS DE VERIFICACIÓN")
        print("="*70 + "\n")
        
        # Tabla comparativa
        print(f"{'Método':<25} {'Overflows':<12} {'1er OF':<10} {'Mag.Max':<10} {'Tiempo(s)':<10}")
        print("-" * 70)
        
        for method, metrics in self.results.items():
            if metrics.get('success', False):
                overflow_count = metrics.get('overflow_count', 'N/A')
                first_of = metrics.get('first_overflow_cycle', 'N/A')
                max_mag = metrics.get('max_magnitude', 'N/A')
                exec_time = metrics.get('execution_time', 'N/A')
                
                if isinstance(exec_time, float):
                    exec_time = f"{exec_time:.2f}"
                
                print(f"{method:<25} {str(overflow_count):<12} {str(first_of):<10} {str(max_mag):<10} {str(exec_time):<10}")
            else:
                print(f"{method:<25} {'FALLÓ':<12} {'-':<10} {'-':<10} {'-':<10}")
        
        print("\n" + "="*70)
        
        # Análisis de eficiencia
        print("\nANÁLISIS DE EFICIENCIA:")
        print("-" * 70)
        
        # Encontrar método más rápido en detectar overflow
        valid_methods = {k: v for k, v in self.results.items() 
                        if v.get('success') and v.get('first_overflow_cycle') is not None}
        
        if valid_methods:
            fastest = min(valid_methods.items(), 
                         key=lambda x: x[1]['first_overflow_cycle'])
            print(f"\n✓ Convergencia más rápida: {fastest[0]}")
            print(f"  Detectó overflow en ciclo: {fastest[1]['first_overflow_cycle']}")
            
            # Calcular speedup respecto a random
            if 'Random' in valid_methods and fastest[0] != 'Random':
                speedup = valid_methods['Random']['first_overflow_cycle'] / fastest[1]['first_overflow_cycle']
                print(f"  Speedup vs Random: {speedup:.2f}x")
        
        # Método con más overflows
        if self.results:
            most_overflows = max(self.results.items(), 
                                key=lambda x: x[1].get('overflow_count', 0))
            print(f"\n✓ Mayor cobertura de overflow: {most_overflows[0]}")
            print(f"  Total overflows: {most_overflows[1].get('overflow_count', 0)}")
            
            # Calcular mejora respecto a random
            if 'Random' in self.results and most_overflows[0] != 'Random':
                if self.results['Random'].get('overflow_count', 0) > 0:
                    improvement = (most_overflows[1].get('overflow_count', 0) / 
                                 self.results['Random'].get('overflow_count', 1))
                    print(f"  Mejora vs Random: {improvement:.2f}x")
        
        print("\n" + "="*70)
    
    def generate_comparison_plots(self):
        """
        Genera gráficos comparativos.
        """
        print("\nGenerando visualizaciones comparativas...")
        
        # Preparar datos
        methods = []
        first_overflows = []
        total_overflows = []
        max_magnitudes = []
        
        for method, metrics in self.results.items():
            if metrics.get('success', False):
                methods.append(method)
                first_overflows.append(metrics.get('first_overflow_cycle', 0))
                total_overflows.append(metrics.get('overflow_count', 0))
                max_magnitudes.append(metrics.get('max_magnitude', 0))
        
        if not methods:
            print("No hay datos suficientes para generar gráficos")
            return
        
        # Crear figura con 3 subplots
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Colores personalizados
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12'][:len(methods)]
        
        # 1. Convergencia (Primer Overflow)
        ax1 = axes[0]
        bars1 = ax1.bar(methods, first_overflows, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Ciclos hasta 1er Overflow', fontsize=11)
        ax1.set_title('Velocidad de Convergencia\n(Menor es Mejor)', fontsize=12, fontweight='bold')
        ax1.set_ylim(0, max(first_overflows) * 1.2 if first_overflows else 100)
        ax1.grid(axis='y', alpha=0.3)
        
        # Añadir valores sobre barras
        for bar, value in zip(bars1, first_overflows):
            height = bar.get_height()
            if value > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(value)}',
                        ha='center', va='bottom', fontweight='bold')
        
        # 2. Total de Overflows
        ax2 = axes[1]
        bars2 = ax2.bar(methods, total_overflows, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_ylabel('Total de Overflows Detectados', fontsize=11)
        ax2.set_title('Cobertura de Corner Cases\n(Mayor es Mejor)', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, max(total_overflows) * 1.2 if total_overflows else 100)
        ax2.grid(axis='y', alpha=0.3)
        
        for bar, value in zip(bars2, total_overflows):
            height = bar.get_height()
            if value > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(value)}',
                        ha='center', va='bottom', fontweight='bold')
        
        # 3. Magnitud Máxima
        ax3 = axes[2]
        bars3 = ax3.bar(methods, max_magnitudes, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_ylabel('Magnitud Máxima Alcanzada', fontsize=11)
        ax3.set_title('Extremos de Salida\n(Mayor es Mejor)', fontsize=12, fontweight='bold')
        ax3.axhline(y=16000, color='red', linestyle='--', linewidth=2, label='Umbral Overflow')
        ax3.set_ylim(0, max(max_magnitudes) * 1.2 if max_magnitudes else 20000)
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        for bar, value in zip(bars3, max_magnitudes):
            height = bar.get_height()
            if value > 0:
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(value)}',
                        ha='center', va='bottom', fontweight='bold')
        
        # Rotar labels si son muy largos
        for ax in axes:
            ax.tick_params(axis='x', rotation=15)
        
        plt.tight_layout()
        
        # Guardar
        output_file = "verification_methods_comparison.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Gráfico comparativo guardado: {output_file}")
        
        # Crear tabla comparativa adicional
        self.create_comparison_table()
    
    def create_comparison_table(self):
        """
        Crea una tabla visual comparativa.
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.axis('tight')
        ax.axis('off')
        
        # Preparar datos para tabla
        headers = ['Método', 'Convergencia\n(ciclos)', 'Total\nOverflows', 
                  'Mag. Máx.', 'Tasa OF\n(%)', 'Tiempo\n(s)']
        
        table_data = []
        for method, metrics in self.results.items():
            if metrics.get('success', False):
                row = [
                    method,
                    str(metrics.get('first_overflow_cycle', '-')),
                    str(metrics.get('overflow_count', '-')),
                    str(metrics.get('max_magnitude', '-')),
                    f"{metrics.get('overflow_rate', 0):.2f}",
                    f"{metrics.get('execution_time', 0):.2f}"
                ]
                table_data.append(row)
        
        # Crear tabla
        table = ax.table(cellText=table_data, colLabels=headers,
                        cellLoc='center', loc='center',
                        colWidths=[0.25, 0.15, 0.15, 0.15, 0.15, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Estilo de header
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#3498db')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Estilo de filas (alternar colores)
        for i in range(1, len(table_data) + 1):
            for j in range(len(headers)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#ecf0f1')
                else:
                    table[(i, j)].set_facecolor('#ffffff')
        
        plt.title('Tabla Comparativa de Métodos de Verificación', 
                 fontsize=14, fontweight='bold', pad=20)
        
        output_file = "verification_comparison_table.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Tabla comparativa guardada: {output_file}")


def main():
    """
    Función principal que ejecuta todos los testbenches y genera comparaciones.
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  Comparación de Métodos de Verificación Funcional               ║
    ║  ML-Guided vs Traditional Random Testing                        ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    comparator = VerificationComparator()
    
    # Definir testbenches a ejecutar
    testbenches = [
        ("test_fir_random", "Random"),
        ("test_fir_ml", "ML-Clasificador"),
        ("test_fir_ml_regressor", "ML-Regresor"),
        ("test_fir_ml_memory", "ML-Temporal")
    ]
    
    # Opción 1: Ejecutar todos
    print("\n¿Desea ejecutar todos los testbenches automáticamente?")
    print("(Esto tomará varios minutos)")
    response = input("Ejecutar todo [s/N]: ").strip().lower()
    
    if response == 's':
        for module, name in testbenches:
            comparator.run_testbench(module, name)
    else:
        # Opción 2: Parsear resultados existentes
        print("\nParseando resultados de ejecuciones previas...")
        print("(Asegúrese de haber ejecutado los testbenches individualmente)")
        
        # Leer archivos de log si existen
        for module, name in testbenches:
            log_file = f"sim_build/sim.log"
            if os.path.exists(log_file):
                print(f"Nota: Encontrado {log_file}, pero parsing manual requerido")
        
        print("\nPara análisis completo, ejecute cada testbench individualmente:")
        for module, name in testbenches:
            print(f"  make SIM=icarus TOPLEVEL=filter MODULE={module}")
    
    # Generar reporte y visualizaciones
    if comparator.results:
        comparator.generate_comparison_report()
        comparator.generate_comparison_plots()
        
        print("\n" + "="*70)
        print("ANÁLISIS COMPLETADO")
        print("="*70)
        print("\nArchivos generados:")
        print("  - verification_methods_comparison.png")
        print("  - verification_comparison_table.png")
    else:
        print("\n⚠ No hay resultados para analizar.")
        print("Ejecute los testbenches individualmente y vuelva a correr este script.")


if __name__ == "__main__":
    main()
