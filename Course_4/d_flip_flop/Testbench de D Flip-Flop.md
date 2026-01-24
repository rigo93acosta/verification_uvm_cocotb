# Testbench de D Flip-Flop con Cocotb

## Descripción General

Este proyecto implementa un testbench de verificación para un D flip-flop digital utilizando Cocotb, una biblioteca de Python para simulación de HDL. El testbench sigue un patrón similar al UVM (Universal Verification Methodology), estructurado en componentes modulares para generar estímulos aleatorios, inyectarlos al DUT, monitorear respuestas y comparar resultados esperados.

## Archivos en la Carpeta

- **dff_tb.py**: Archivo principal del testbench en Python. Contiene las clases del testbench y la función de prueba principal.
- **makefile**: Archivo de construcción para compilar y ejecutar la simulación usando Icarus Verilog y Cocotb.
- **dff.sv**: Módulo Verilog del Device Under Test (DUT), un D flip-flop síncrono con reset.
- **dump.vcd**: Archivo de ondas generado por la simulación (creado después de ejecutar).

## Descripción del DUT

El DUT es un módulo Verilog llamado `dff` que implementa un flip-flop D síncrono con reset asíncrono. La salida `dout` se actualiza en el flanco positivo del reloj `clk` con el valor de `din`, a menos que `rst` esté activo, en cuyo caso `dout` se resetea a 0. Es un circuito secuencial, y se simula usando Icarus Verilog.

### Entity: dff 
- **File**: dff.sv

### Diagram
![Diagram](dff.svg "Diagram")
### Ports

| Port name | Direction | Type  | Description |
| --------- | --------- | ----- | ----------- |
| clk       | input     |       | Reloj de entrada |
| rst       | input     |       | Reset asíncrono (activo alto) |
| din       | input     |       | Dato de entrada |
| dout      | output    | reg   | Dato de salida |

## Proceso de Verificación (Patrón UVM-like)

El testbench sigue un flujo de verificación estructurado similar a UVM, dividido en las siguientes fases/componentes:

1. **Transaction**: Clase que representa los datos de entrada/salida (din, dout). Incluye randomización para generar estímulos aleatorios.

2. **Generator**: Genera transacciones aleatorias y las envía a una cola. Espera eventos para sincronizar con el scoreboard.

3. **Driver**: Recibe transacciones de la cola y las aplica a las entradas del DUT. Aplica reset inicial y maneja la señalización de `din` en flancos de reloj.

4. **Monitor**: Muestrea las salidas del DUT y las entradas actuales en flancos de reloj, creando transacciones de respuesta que envía al scoreboard.

5. **Scoreboard**: Compara los resultados muestreados con los valores esperados (dout debe igualar din del ciclo anterior, considerando reset). Registra PASS/FAIL y notifica al generator para continuar.

El flujo es asíncrono y concurrente, con tareas corriendo en paralelo usando `cocotb.start_soon`.

## Detalles de Timing

El timing en la simulación está controlado por flancos de reloj y ciclos de reloj de Cocotb para asegurar la sincronización correcta con el DUT secuencial:

- **Driver**: Aplica reset durante 5 ciclos de reloj. Luego, para cada transacción, establece `din` y espera un flanco de reloj positivo para que el DUT capture el valor. Opcionalmente, limpia `din` después de otro flanco.
- **Monitor**: Espera flancos de reloj positivos para muestrear `dout` (que se actualiza en el flanco). Muestrea `din` actual y envía la transacción.
- **Test Principal**: Corre por `Timer(200, unit="ns")`, suficiente para 10 pruebas con un reloj de 10ns de período (aprox. 20 ciclos de reloj).

Esto asegura que la verificación se sincronice correctamente con el comportamiento secuencial del flip-flop, evitando muestreo prematuro o tardío.

## Cómo Ejecutar

1. Asegúrate de tener el entorno virtual activado: `source .venv/bin/activate` (usando uv).
2. En el directorio del proyecto: `cd Course_4/d_flip_flop`
3. Ejecuta: `make`
4. Revisa los logs en la consola y el archivo `dump.vcd` para ver los resultados en gtkwave.

## Dependencias

- Python >= 3.12
- Cocotb >= 2.0.1
- Cocotb-bus >= 0.3.0
- Cocotb-coverage >= 2.0
- Icarus Verilog (para simulación HDL)
- Gtkwave (para visualizar archivos VCD)

Este setup permite una verificación automatizada y reproducible del D flip-flop.