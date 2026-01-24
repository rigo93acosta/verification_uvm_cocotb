# Testbench de SPI Master con Cocotb

## Descripción General

Este proyecto implementa un testbench de verificación para un módulo SPI Master (Serial Peripheral Interface) digital utilizando Cocotb, una biblioteca de Python para simulación de HDL. El testbench sigue un patrón similar al UVM (Universal Verification Methodology), estructurado en componentes modulares para generar estímulos aleatorios, inyectarlos al DUT, monitorear respuestas y comparar resultados esperados.

**Nota**: Esta es la primera parte del proyecto SPI, donde solo se implementa y verifica el **Master**. Falta implementar y verificar el **Slave** en una fase posterior.

## Archivos en la Carpeta

- **spi_tb.py**: Archivo principal del testbench en Python. Contiene las clases del testbench y la función de prueba principal.
- **makefile**: Archivo de construcción para compilar y ejecutar la simulación usando Icarus Verilog y Cocotb.
- **spi_my.sv**: Módulo SystemVerilog del Device Under Test (DUT), un SPI Master que serializa datos de 12 bits.
- **spi.sv**: Archivo de solución del curso (no utilizado actualmente).
- **waveform_spi.vcd**: Archivo de ondas generado por la simulación (creado después de ejecutar).

## Descripción del DUT

El DUT es un módulo SystemVerilog llamado `SPI` que implementa un **SPI Master** capaz de transmitir datos de 12 bits en serie. El módulo genera su propia señal de reloj SPI (`sclk`) derivada del reloj del sistema, y utiliza una máquina de estados para controlar la transmisión. Los datos se envían MSB first (bit más significativo primero) a través de la señal `mosi` (Master Out Slave In). La señal `cs` (Chip Select) se activa (baja) durante la transmisión.

### Entity: SPI
- **File**: spi_my.sv

### Ports

| Port name | Direction | Type   | Description |
| --------- | --------- | ------ | ----------- |
| clk       | input     |        | Reloj del sistema (100 MHz) |
| rst       | input     |        | Reset síncrono (activo alto) |
| newd      | input     |        | Nueva solicitud de dato (activo alto) |
| din       | input     | [11:0] | Dato de entrada a transmitir (12 bits) |
| sclk      | output    | reg    | Reloj SPI generado (~5 MHz, divide por 20) |
| mosi      | output    | reg    | Master Out Slave In - línea de datos serial |
| cs        | output    | reg    | Chip Select (activo bajo durante transmisión) |

### Características del Diseño

- **Generación de SCLK**: El reloj SPI se genera dividiendo el reloj del sistema. `sclk` oscila cada 10 ciclos de `clk` (countc), creando una frecuencia aproximada de 5 MHz. Importante: `sclk` solo oscila cuando `cs = 0` (durante transmisión activa), permaneciendo en `0` cuando está inactivo.

- **Máquina de Estados**: 
  - **idle**: Estado de reposo. `cs = 1`, esperando señal `newd = 1` para iniciar transmisión.
  - **send**: Estado de transmisión. Envía los 12 bits secuencialmente en cada flanco positivo de `sclk` (detectado internamente), MSB first.

- **Temporización**: Utiliza un contador interno `count` para rastrear los bits transmitidos (0-11) y un contador `countc` para generar `sclk`.

- **Detección de Edges de SCLK**: Para evitar problemas de timing/skew, se utiliza un `wire` (`sclk_edge`) que combina las condiciones `countc == 10 && sclk == 1'b1`. Esto permite que la máquina de estados se ejecute en `@(posedge clk)` (reloj del sistema) en lugar de `@(posedge sclk)`, previniendo violaciones de timing cuando `sclk` no está perfectamente sincronizado con el reloj del sistema. En contraste, implementaciones que usan `@(posedge sclk)` directamente pueden sufrir de skew de tiempo, especialmente en diseños donde `sclk` se genera internamente.

## Proceso de Verificación (Patrón UVM-like)

El testbench sigue un flujo de verificación estructurado similar a UVM, dividido en las siguientes fases/componentes:

1. **Transaction**: Clase que representa los datos de entrada/salida del SPI (`newd`, `din`, `sclk`, `mosi`, `cs`, `dout`). Incluye randomización para generar valores aleatorios de `din` (rango 0-4095, 12 bits) usando `cocotb_coverage.crv.Randomized`.

2. **Generator**: Genera transacciones aleatorias (configuradas para `count=5` pruebas) y las envía a una cola (`drv_queue`). Espera eventos del scoreboard para sincronizar y controlar el ritmo de generación.

3. **Driver**: Recibe transacciones de la cola y las aplica a las entradas del DUT. Maneja:
   - **reset_dut**: Aplica reset durante 5 ciclos de reloj, estableciendo `din = 0` y `newd = 0`.
   - **recv_data**: Para cada transacción, aplica `din`, genera un pulso de `newd` de 1 ciclo de `clk`, y espera el rising edge de `cs` (fin de transmisión) antes de procesar la siguiente.

4. **Monitor**: Muestrea la transmisión SPI en tiempo real:
   - Espera el falling edge de `cs` (inicio de operación).
   - Captura el valor de `din` actual.
   - Sincroniza con rising edges de `sclk` para reconstruir los 12 bits transmitidos en `mosi`, reconstruyendo `dout` mediante shift left y OR.
   - Espera el rising edge de `cs` (fin de operación) y envía la transacción completa al scoreboard.

5. **Scoreboard**: Compara los datos transmitidos (`din`) con los datos recibidos/reconstruidos (`dout`):
   - Recibe transacciones del monitor.
   - Verifica que `din == dout`. Registra **Match** (PASS) o **Mismatch** (FAIL).
   - Notifica al generator mediante un evento para continuar con la siguiente transacción.

El flujo es asíncrono y concurrente, con tareas corriendo en paralelo usando `cocotb.start_soon`.

## Detalles de Timing

El timing en la simulación está cuidadosamente coordinado para sincronizar correctamente con el comportamiento del DUT secuencial:

- **Clock del Sistema**: Generado a 10 ns de período (100 MHz) usando `Clock(dut.clk, 10, unit="ns")`.

- **SCLK**: Generado internamente por el DUT. Oscila cada 10 ciclos de `clk`, resultando en un período de aproximadamente 200 ns (~5 MHz). Solo oscila cuando `cs = 0`.

- **Driver**: 
  - Aplica reset durante 5 ciclos de reloj del sistema.
  - Genera un pulso de `newd` de exactamente 1 ciclo de `clk` para iniciar cada transmisión.
  - Espera `RisingEdge(cs)` para confirmar que la transmisión ha terminado antes de procesar la siguiente transacción.

- **Monitor**: 
  - Se sincroniza con `FallingEdge(cs)` para detectar el inicio de cada operación.
  - Muestrea en `RisingEdge(sclk)` para capturar cada bit de `mosi` de forma confiable.
  - Total de 13 rising edges de `sclk` (1 inicial para sincronización + 12 para capturar datos).

- **Duración del Test**: 15000 ns (15 µs), suficiente para completar 5 transacciones. Cada transacción SPI completa toma aproximadamente 12 bits × 200 ns/bit = 2400 ns, más overhead de sincronización.

**Consideraciones Críticas de Sincronización**:
- El `sclk` debe estar controlado por `cs` para evitar bloqueos entre transacciones.
- El monitor no debe esperar rising edges de `sclk` cuando `cs = 1` (idle), ya que `sclk` está detenido.
- El driver debe generar pulsos cortos de `newd` (1 ciclo) en lugar de mantenerlo alto.

## Cómo Ejecutar

1. Asegúrate de tener el entorno virtual activado: `source .venv/bin/activate` (usando uv).
2. En el directorio del proyecto: `cd Course_4/spi`
3. Ejecuta: `make`
4. Revisa los logs en la consola para ver los resultados de las comparaciones (Match/Mismatch).
5. Visualiza el archivo `waveform_spi.vcd` en gtkwave para analizar las formas de onda:
   ```bash
   gtkwave waveform_spi.vcd
   ```
   ![Waveform](waveform.png "Waveform SPI Master")

## Dependencias

- Python >= 3.12
- Cocotb >= 2.0.1
- Cocotb-bus >= 0.3.0
- Cocotb-coverage >= 2.0 (para randomización con crv)
- Icarus Verilog (para simulación HDL)
- Gtkwave (para visualizar archivos VCD)

## Próximos Pasos

Esta implementación verifica únicamente el **SPI Master**. Los siguientes pasos incluyen:
1. Implementar un módulo **SPI Slave** en SystemVerilog.
2. Conectar Master y Slave en un sistema completo.
3. Extender el testbench para verificar la comunicación bidireccional completa.
4. Agregar verificación de protocolo y casos de error (e.g., violaciones de timing, estados inválidos).

Este setup permite una verificación automatizada y reproducible del SPI Master, estableciendo las bases para un sistema SPI completo.
