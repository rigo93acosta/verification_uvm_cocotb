"""
SPI System Verification usando ML para GENERACIÓN INTELIGENTE DE SECUENCIAS

OBJETIVO PRINCIPAL:
- Reducir el espacio de secuencias posibles (millones → cientos)
- Generar secuencias que MAXIMICEN la cobertura funcional
- Evitar secuencias redundantes
- Encontrar casos corner automáticamente

ML se usa para OPTIMIZAR qué secuencias probar, no para predecir comportamiento.
"""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock
import random
import numpy as np
from collections import defaultdict


# ==============================================================================
# CLASE AUXILIAR PARA TRANSACCIONES SPI
# ==============================================================================

class SPITransaction:
    """Representa una transacción SPI con todos sus detalles"""
    def __init__(self, slave_id: int, tx_data: int, rx_data: int, cycles: int):
        self.slave_id = slave_id
        self.tx_data = tx_data
        self.rx_data = rx_data
        self.cycles = cycles


# ==============================================================================
# COBERTURA FUNCIONAL
# ==============================================================================

class CoverageMetrics:
    """
    Define y rastrea cobertura funcional del sistema SPI
    """
    
    def __init__(self):
        # Bins de cobertura
        self.slave_access = defaultdict(int)  # Accesos por esclavo
        self.transitions = defaultdict(int)   # Transiciones S0->S1, S1->S0, etc
        self.data_ranges = defaultdict(int)   # Rangos de datos: 0x00-0x3F, 0x40-0x7F, etc
        self.sequence_patterns = defaultdict(int)  # Patrones de 3 transacciones
        self.corner_cases = defaultdict(int)  # Casos especiales
        
        self.total_transactions = 0
        
    def update(self, sequence):
        """
        Actualiza cobertura con una secuencia de transacciones
        sequence: lista de (slave_id, data)
        """
        self.total_transactions += len(sequence)
        
        for slave_id, data in sequence:
            # Cobertura: accesos a cada esclavo
            self.slave_access[slave_id] += 1
            
            # Cobertura: rangos de datos
            data_bin = data // 64  # 0-63, 64-127, 128-191, 192-255
            self.data_ranges[f"slave{slave_id}_range{data_bin}"] += 1
            
            # Cobertura: corner cases
            if data == 0x00:
                self.corner_cases[f"slave{slave_id}_zero"] += 1
            elif data == 0xFF:
                self.corner_cases[f"slave{slave_id}_max"] += 1
            elif data == 0xAA:
                self.corner_cases[f"slave{slave_id}_pattern_AA"] += 1
            elif data == 0x55:
                self.corner_cases[f"slave{slave_id}_pattern_55"] += 1
        
        # Cobertura: transiciones entre esclavos
        for i in range(len(sequence) - 1):
            curr_slave = sequence[i][0]
            next_slave = sequence[i + 1][0]
            self.transitions[f"S{curr_slave}->S{next_slave}"] += 1
        
        # Cobertura: patrones de secuencia (3 elementos)
        if len(sequence) >= 3:
            for i in range(len(sequence) - 2):
                pattern = tuple(s[0] for s in sequence[i:i+3])
                self.sequence_patterns[pattern] += 1
    
    def get_coverage_percentage(self):
        """Calcula porcentaje de cobertura alcanzado"""
        # Definir bins esperados
        expected_bins = {
            'slaves': 2,  # Slave 0, Slave 1
            'transitions': 4,  # S0->S0, S0->S1, S1->S0, S1->S1
            'data_ranges': 8,  # 4 rangos × 2 slaves
            'corner_cases': 8,  # 4 corners × 2 slaves
            'patterns': 8,  # Al menos 8 patrones diferentes
        }
        
        coverage = {
            'slaves': len(self.slave_access) / expected_bins['slaves'] * 100,
            'transitions': len(self.transitions) / expected_bins['transitions'] * 100,
            'data_ranges': len(self.data_ranges) / expected_bins['data_ranges'] * 100,
            'corner_cases': len(self.corner_cases) / expected_bins['corner_cases'] * 100,
            'patterns': min(len(self.sequence_patterns) / expected_bins['patterns'] * 100, 100),
        }
        
        # Promedio ponderado
        total_coverage = sum(coverage.values()) / len(coverage)
        
        return total_coverage, coverage
    
    def get_uncovered_items(self):
        """Retorna items que aún no se han cubierto"""
        uncovered = []
        
        # Slaves no accedidos
        for slave_id in [0, 1]:
            if slave_id not in self.slave_access:
                uncovered.append(f"slave_{slave_id}")
        
        # Transiciones faltantes
        for s1 in [0, 1]:
            for s2 in [0, 1]:
                trans = f"S{s1}->S{s2}"
                if trans not in self.transitions:
                    uncovered.append(trans)
        
        # Rangos de datos faltantes
        for slave_id in [0, 1]:
            for bin_id in range(4):
                key = f"slave{slave_id}_range{bin_id}"
                if key not in self.data_ranges:
                    uncovered.append(key)
        
        # Corner cases faltantes
        for slave_id in [0, 1]:
            for corner in ['zero', 'max', 'pattern_AA', 'pattern_55']:
                key = f"slave{slave_id}_{corner}"
                if key not in self.corner_cases:
                    uncovered.append(key)
        
        return uncovered
    
    def print_report(self):
        """Imprime reporte de cobertura"""
        total_cov, detailed_cov = self.get_coverage_percentage()
        
        print(f"\n{'='*70}")
        print(f"REPORTE DE COBERTURA")
        print(f"{'='*70}")
        print(f"Total de transacciones: {self.total_transactions}")
        print(f"\nCobertura por categoría:")
        for category, percentage in detailed_cov.items():
            bar = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
            print(f"  {category:15s}: [{bar}] {percentage:5.1f}%")
        print(f"\n{'─'*70}")
        print(f"COBERTURA TOTAL: {total_cov:.1f}%")
        print(f"{'='*70}\n")
        
        return total_cov


# ==============================================================================
# GENERADOR DE SECUENCIAS CON ML
# ==============================================================================

class MLSequenceGenerator:
    """
    Generador de secuencias usando algoritmo genético simple
    Optimiza secuencias para maximizar cobertura
    """
    
    def __init__(self, population_size=20, sequence_length=10):
        self.population_size = population_size
        self.sequence_length = sequence_length
        self.population = []
        self.best_sequences = []
        
    def generate_random_sequence(self):
        """Genera una secuencia aleatoria"""
        sequence = []
        for _ in range(self.sequence_length):
            slave_id = random.randint(0, 1)
            data = random.randint(0, 255)
            sequence.append((slave_id, data))
        return sequence
    
    def initialize_population(self):
        """Inicializa población con secuencias aleatorias"""
        self.population = [self.generate_random_sequence() 
                          for _ in range(self.population_size)]
    
    def evaluate_fitness(self, sequence):
        """
        Evalúa qué tan buena es una secuencia
        Fitness = cobertura que aporta
        """
        coverage = CoverageMetrics()
        coverage.update(sequence)
        total_cov, _ = coverage.get_coverage_percentage()
        
        # Bonus por diversidad
        unique_slaves = len(set(s[0] for s in sequence))
        unique_data_ranges = len(set(s[1] // 64 for s in sequence))
        
        fitness = total_cov + (unique_slaves * 5) + (unique_data_ranges * 2)
        return fitness
    
    def crossover(self, parent1, parent2):
        """Cruza dos secuencias padres"""
        crossover_point = random.randint(1, self.sequence_length - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child
    
    def mutate(self, sequence, mutation_rate=0.2):
        """Muta una secuencia"""
        mutated = sequence.copy()
        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                # Mutar: cambiar slave o data
                if random.random() < 0.5:
                    mutated[i] = (1 - mutated[i][0], mutated[i][1])  # Cambiar slave
                else:
                    mutated[i] = (mutated[i][0], random.randint(0, 255))  # Cambiar data
        return mutated
    
    def evolve(self, generations=10):
        """
        Evoluciona la población durante N generaciones
        Retorna las mejores secuencias
        """
        self.initialize_population()
        
        for gen in range(generations):
            # Evaluar fitness de toda la población
            fitness_scores = [(seq, self.evaluate_fitness(seq)) 
                            for seq in self.population]
            
            # Ordenar por fitness (mejor primero)
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Seleccionar mejores (elitismo)
            elite_count = self.population_size // 4
            next_generation = [seq for seq, _ in fitness_scores[:elite_count]]
            
            # Generar nueva población mediante crossover y mutación
            while len(next_generation) < self.population_size:
                # Selección por torneo
                parent1 = random.choice(fitness_scores[:self.population_size // 2])[0]
                parent2 = random.choice(fitness_scores[:self.population_size // 2])[0]
                
                # Crossover
                child = self.crossover(parent1, parent2)
                
                # Mutación
                child = self.mutate(child)
                
                next_generation.append(child)
            
            self.population = next_generation
            
            best_fitness = fitness_scores[0][1]
            if (gen + 1) % 5 == 0:
                print(f"  Generación {gen+1}/{generations}: Mejor fitness = {best_fitness:.2f}")
        
        # Retornar top 5 mejores secuencias
        final_scores = [(seq, self.evaluate_fitness(seq)) for seq in self.population]
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        self.best_sequences = [seq for seq, _ in final_scores[:5]]
        return self.best_sequences
    
    def generate_coverage_driven_sequence(self, uncovered_items):
        """
        Genera una secuencia específicamente para cubrir items faltantes
        """
        sequence = []
        
        for item in uncovered_items[:self.sequence_length]:
            if 'slave_' in item and '->' not in item:
                # Necesitamos acceder a un slave específico
                slave_id = int(item.split('_')[1])
                data = random.randint(0, 255)
                sequence.append((slave_id, data))
            
            elif 'range' in item:
                # Necesitamos un rango de datos específico
                parts = item.split('_')
                slave_id = int(parts[0].replace('slave', ''))
                range_id = int(parts[1].replace('range', ''))
                data = random.randint(range_id * 64, (range_id + 1) * 64 - 1)
                sequence.append((slave_id, data))
            
            elif 'zero' in item:
                # Extraer slave_id de forma segura (e.g., 'slave0_zero' -> 0)
                slave_str = item.split('_')[0].replace('slave', '')
                slave_id = int(slave_str) if slave_str else 0
                sequence.append((slave_id, 0x00))
            
            elif 'max' in item:
                slave_str = item.split('_')[0].replace('slave', '')
                slave_id = int(slave_str) if slave_str else 0
                sequence.append((slave_id, 0xFF))
            
            elif 'pattern_AA' in item:
                slave_str = item.split('_')[0].replace('slave', '')
                slave_id = int(slave_str) if slave_str else 0
                sequence.append((slave_id, 0xAA))
            
            elif 'pattern_55' in item:
                slave_str = item.split('_')[0].replace('slave', '')
                slave_id = int(slave_str) if slave_str else 0
                sequence.append((slave_id, 0x55))
        
        # Rellenar hasta completar la longitud
        while len(sequence) < self.sequence_length:
            sequence.append((random.randint(0, 1), random.randint(0, 255)))
        
        return sequence


# ==============================================================================
# FUNCIONES DE UTILIDAD PARA COCOTB
# ==============================================================================

async def spi_write_read(dut, slave_id, tx_data):
    """Realiza una transacción SPI completa"""
    start_cycle = 0
    
    # Esperar a que master esté listo
    while dut.tx_ready.value == 0:
        await RisingEdge(dut.clk)
        start_cycle += 1
        if start_cycle > 100:
            raise Exception("Timeout esperando tx_ready")
    
    # Iniciar transacción
    dut.slave_select.value = slave_id
    dut.tx_data.value = tx_data
    dut.tx_valid.value = 1
    
    await RisingEdge(dut.clk)
    dut.tx_valid.value = 0
    
    # Esperar rx_valid
    cycles = 0
    while dut.rx_valid.value == 0:
        await RisingEdge(dut.clk)
        cycles += 1
        if cycles > 500:
            raise Exception("Timeout esperando rx_valid")
    
    rx_data = int(dut.rx_data.value)
    
    # Esperar un poco más
    await ClockCycles(dut.clk, 5)
    
    return rx_data


async def execute_sequence(dut, sequence):
    """Ejecuta una secuencia completa de transacciones SPI"""
    results = []
    for slave_id, tx_data in sequence:
        rx_data = await spi_write_read(dut, slave_id, tx_data)
        results.append((slave_id, tx_data, rx_data))
    return results


# ==============================================================================
# TESTS DE COCOTB
# ==============================================================================

@cocotb.test()
async def test_ml_sequence_generation(dut):
    """
    Test principal: Compara Random vs ML-Guided sequence generation
    Demuestra cómo ML reduce el espacio de pruebas y maximiza cobertura
    """
    
    cocotb.log.info("="*80)
    cocotb.log.info("VERIFICACIÓN SPI: Random vs ML-Guided Sequence Generation")
    cocotb.log.info("="*80)
    
    # Iniciar clock y reset
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    dut.rst_n.value = 0
    dut.tx_valid.value = 0
    dut.tx_data.value = 0
    dut.slave_select.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    cocotb.log.info("Reset completado\n")
    
    # ==========================================================================
    # ESTRATEGIA 1: SECUENCIAS RANDOM (baseline)
    # ==========================================================================
    cocotb.log.info("[ESTRATEGIA 1] Generación RANDOM de secuencias")
    cocotb.log.info("-"*80)
    
    random_coverage = CoverageMetrics()
    num_random_sequences = 10
    sequence_length = 10
    
    cocotb.log.info(f"Ejecutando {num_random_sequences} secuencias random de {sequence_length} transacciones cada una")
    cocotb.log.info(f"Total de transacciones: {num_random_sequences * sequence_length}\n")
    
    for i in range(num_random_sequences):
        # Generar secuencia random
        sequence = []
        for _ in range(sequence_length):
            slave_id = random.randint(0, 1)
            data = random.randint(0, 255)
            sequence.append((slave_id, data))
        
        # Ejecutar en DUT
        await execute_sequence(dut, sequence)
        
        # Actualizar cobertura
        random_coverage.update(sequence)
    
    cocotb.log.info("Resultados RANDOM:")
    random_total_cov = random_coverage.print_report()
    
    # ==========================================================================
    # ESTRATEGIA 2: SECUENCIAS GENERADAS POR ML (Algoritmo Genético)
    # ==========================================================================
    cocotb.log.info("\n[ESTRATEGIA 2] Generación con ML (Algoritmo Genético)")
    cocotb.log.info("-"*80)
    
    cocotb.log.info("Entrenando generador ML...")
    cocotb.log.info("Optimizando secuencias mediante algoritmo genético:\n")
    
    ml_generator = MLSequenceGenerator(population_size=20, sequence_length=10)
    best_sequences = ml_generator.evolve(generations=20)
    
    cocotb.log.info(f"\n✓ ML generó {len(best_sequences)} secuencias optimizadas\n")
    
    ml_coverage = CoverageMetrics()
    
    cocotb.log.info(f"Ejecutando {len(best_sequences)} secuencias ML-guided...")
    
    for i, sequence in enumerate(best_sequences):
        # Ejecutar en DUT
        await execute_sequence(dut, sequence)
        
        # Actualizar cobertura
        ml_coverage.update(sequence)
    
    cocotb.log.info("Resultados ML-GUIDED:")
    ml_total_cov = ml_coverage.print_report()
    
    # ==========================================================================
    # ESTRATEGIA 3: COBERTURA DIRIGIDA (Coverage-Driven)
    # ==========================================================================
    cocotb.log.info("\n[ESTRATEGIA 3] Refinamiento con Coverage-Driven Generation")
    cocotb.log.info("-"*80)
    
    # Identificar qué falta cubrir
    uncovered = ml_coverage.get_uncovered_items()
    
    if uncovered:
        cocotb.log.info(f"Items sin cubrir detectados: {len(uncovered)}")
        cocotb.log.info(f"Ejemplos: {uncovered[:5]}\n")
        
        # Generar secuencias específicas para cubrir lo faltante
        cocotb.log.info("Generando secuencias dirigidas para cubrir gaps...")
        
        num_directed_sequences = min(5, (len(uncovered) + 9) // 10)
        
        for i in range(num_directed_sequences):
            sequence = ml_generator.generate_coverage_driven_sequence(uncovered)
            await execute_sequence(dut, sequence)
            ml_coverage.update(sequence)
            
            # Recalcular items sin cubrir
            uncovered = ml_coverage.get_uncovered_items()
        
        cocotb.log.info("\nResultados FINALES (ML + Coverage-Driven):")
        final_cov = ml_coverage.print_report()
    else:
        cocotb.log.info("✓ Cobertura completa alcanzada!\n")
        final_cov = ml_total_cov
    
    # ==========================================================================
    # COMPARACIÓN Y RESULTADOS
    # ==========================================================================
    cocotb.log.info("\n" + "="*80)
    cocotb.log.info("COMPARACIÓN: Random vs ML-Guided")
    cocotb.log.info("="*80)
    
    random_trans = random_coverage.total_transactions
    ml_trans = ml_coverage.total_transactions
    
    cocotb.log.info(f"\nMétrica                     │ Random          │ ML-Guided       │ Mejora")
    cocotb.log.info(f"─"*80)
    cocotb.log.info(f"Cobertura alcanzada         │ {random_total_cov:6.2f}%        │ {final_cov:6.2f}%        │ +{final_cov - random_total_cov:.2f}%")
    cocotb.log.info(f"Transacciones ejecutadas    │ {random_trans:6d}          │ {ml_trans:6d}          │ {ml_trans - random_trans:+6d}")
    
    efficiency_random = random_total_cov / random_trans if random_trans > 0 else 0
    efficiency_ml = final_cov / ml_trans if ml_trans > 0 else 0
    
    cocotb.log.info(f"Eficiencia (cov/trans)      │ {efficiency_random:6.4f}        │ {efficiency_ml:6.4f}        │ {((efficiency_ml/efficiency_random - 1) * 100) if efficiency_random > 0 else 0:+6.1f}%")
    
    cocotb.log.info("\n" + "="*80)
    cocotb.log.info("CONCLUSIÓN:")
    cocotb.log.info("="*80)
    
    if final_cov > random_total_cov:
        improvement = final_cov - random_total_cov
        cocotb.log.info(f"✓ ML-Guided logró {improvement:.1f}% más de cobertura")
        cocotb.log.info(f"✓ ML reduce el espacio de pruebas generando secuencias más efectivas")
        cocotb.log.info(f"✓ Menos transacciones para alcanzar mejor cobertura = Verificación más eficiente")
    else:
        cocotb.log.info(f"⚠ En este run, random tuvo resultados similares")
        cocotb.log.info(f"  (ML típicamente mejora con sistemas más complejos)")
    
    cocotb.log.info("="*80 + "\n")
    
    # Validación
    assert ml_coverage.total_transactions > 0, "No se ejecutaron transacciones ML"
    assert final_cov >= random_total_cov * 0.9, "ML no debe ser significativamente peor que random"


@cocotb.test()
async def test_corner_case_coverage(dut):
    """Test enfocado en cubrir casos corner usando ML"""
    
    cocotb.log.info("\n" + "="*80)
    cocotb.log.info("Test: Cobertura de Corner Cases con ML")
    cocotb.log.info("="*80)
    
    # Setup
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    dut.rst_n.value = 0
    dut.tx_valid.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    coverage = CoverageMetrics()
    
    # Generar secuencias enfocadas en corners
    corner_sequences = [
        [(0, 0x00), (1, 0x00), (0, 0xFF), (1, 0xFF)],  # Min/Max
        [(0, 0xAA), (1, 0x55), (0, 0xAA), (1, 0x55)],  # Patterns
        [(0, 0x01), (0, 0x02), (0, 0x04), (0, 0x08)],  # Powers of 2
        [(1, 0x00), (1, 0xFF), (1, 0xAA), (1, 0x55)],  # Same slave
    ]
    
    for i, sequence in enumerate(corner_sequences):
        cocotb.log.info(f"Ejecutando secuencia corner {i+1}/{len(corner_sequences)}")
        await execute_sequence(dut, sequence)
        coverage.update(sequence)
    
    total_cov, detailed = coverage.get_coverage_percentage()
    
    cocotb.log.info(f"\nCobertura de corner cases: {detailed['corner_cases']:.1f}%")
    cocotb.log.info(f"Cobertura total: {total_cov:.1f}%\n")
    
    assert detailed['corner_cases'] >= 75.0, "Debe cubrir al menos 75% de corner cases"


@cocotb.test()
async def test_transition_coverage(dut):
    """Test enfocado en transiciones entre estados"""
    
    cocotb.log.info("\n" + "="*80)
    cocotb.log.info("Test: Cobertura de Transiciones")
    cocotb.log.info("="*80)
    
    # Setup
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    dut.rst_n.value = 0
    dut.tx_valid.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    coverage = CoverageMetrics()
    
    # Secuencias diseñadas para cubrir todas las transiciones
    transition_sequences = [
        [(0, 0x10), (0, 0x20), (0, 0x30)],  # S0->S0->S0
        [(1, 0x10), (1, 0x20), (1, 0x30)],  # S1->S1->S1
        [(0, 0x10), (1, 0x20), (0, 0x30)],  # S0->S1->S0
        [(1, 0x10), (0, 0x20), (1, 0x30)],  # S1->S0->S1
    ]
    
    for sequence in transition_sequences:
        await execute_sequence(dut, sequence)
        coverage.update(sequence)
    
    total_cov, detailed = coverage.get_coverage_percentage()
    
    cocotb.log.info(f"\nCobertura de transiciones: {detailed['transitions']:.1f}%")
    cocotb.log.info(f"Transiciones cubiertas: {len(coverage.transitions)}/4")
    
    for trans, count in coverage.transitions.items():
        cocotb.log.info(f"  {trans}: {count} veces")
    
    assert detailed['transitions'] == 100.0, "Debe cubrir todas las transiciones"


# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

async def spi_write_read(dut, slave_id, tx_data):
    """Realiza una transacción SPI completa y retorna los datos recibidos"""
    start_cycle = 0
    
    # Esperar a que master esté listo
    while dut.tx_ready.value == 0:
        await RisingEdge(dut.clk)
        start_cycle += 1
        if start_cycle > 100:
            raise Exception("Timeout esperando tx_ready")
    
    # Iniciar transacción
    dut.slave_select.value = slave_id
    dut.tx_data.value = tx_data
    dut.tx_valid.value = 1
    
    await RisingEdge(dut.clk)
    dut.tx_valid.value = 0
    
    # Esperar rx_valid
    cycles = 0
    while dut.rx_valid.value == 0:
        await RisingEdge(dut.clk)
        cycles += 1
        if cycles > 500:
            raise Exception("Timeout esperando rx_valid")
    
    rx_data = int(dut.rx_data.value)
    await ClockCycles(dut.clk, 5)
    
    return SPITransaction(slave_id, tx_data, rx_data, cycles)


async def execute_sequence(dut, sequence):
    """Ejecuta una secuencia completa de transacciones SPI"""
    for slave_id, tx_data in sequence:
        await spi_write_read(dut, slave_id, tx_data)


@cocotb.test()
async def test_sequential_slave(dut):
    """Test de múltiples transacciones al mismo esclavo"""
    
    cocotb.log.info("\n" + "="*80)
    cocotb.log.info("Test: Transacciones Secuenciales al Mismo Esclavo")
    cocotb.log.info("="*80)
    
    # Setup
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    
    dut.rst_n.value = 0
    dut.tx_valid.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Enviar 5 transacciones consecutivas al slave 0
    cocotb.log.info("\nEnviando a Slave 0:")
    for i in range(5):
        tx_data = 0x20 + i
        trans = await spi_write_read(dut, 0, tx_data)
        cocotb.log.info(f"  TX:0x{tx_data:02X} → RX:0x{trans.rx_data:02X}")
    
    # Enviar 5 transacciones consecutivas al slave 1
    cocotb.log.info("\nEnviando a Slave 1:")
    for i in range(5):
        tx_data = 0x30 + i
        trans = await spi_write_read(dut, 1, tx_data)
        cocotb.log.info(f"  TX:0x{tx_data:02X} → RX:0x{trans.rx_data:02X}")
    
    cocotb.log.info("\n✓ Test de transacciones secuenciales completado")
