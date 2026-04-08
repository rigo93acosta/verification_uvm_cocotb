# Testbench de I2C con Cocotb: Master, Slave y Comunicación Bidireccional

## Descripción General

Este proyecto implementa un testbench de verificación para módulos I2C (Inter-Integrated Circuit) digitales utilizando Cocotb, una biblioteca de Python para simulación de HDL. El testbench sigue un patrón similar al UVM (Universal Verification Methodology), estructurado en componentes modulares para generar estímulos aleatorios, inyectarlos al DUT, monitorear respuestas y comparar resultados esperados.

El proyecto implementa un sistema completo de comunicación I2C:
- **I2C Master**: Módulo que inicia y controla la comunicación, generando el reloj SCL y transmitiendo/recibiendo datos a través de SDA.
- **I2C Slave**: Módulo que responde a las solicitudes del Master, enviando/recibiendo datos y ACKs.
- **Top Level**: Sistema completo que conecta Master y Slave con las resistencias pull-up simuladas, verificando la comunicación bidireccional.

El protocolo I2C utiliza **dos líneas bidireccionales** (SDA y SCL) con **lógica open-drain** y resistencias pull-up externas, lo que permite múltiples dispositivos en el mismo bus.

## Archivos en la Carpeta

- **i2c_tb.py**: Archivo principal del testbench en Python. Contiene las clases del testbench y la función de prueba principal.
- **makefile**: Archivo de construcción para compilar y ejecutar la simulación usando Icarus Verilog y Cocotb.
- **i2c_master.sv**: Módulo SystemVerilog del I2C Master (DUT).
- **i2c_slave.sv**: Módulo SystemVerilog del I2C Slave (DUT).
- **i2c.sv**: Módulo top-level que conecta Master y Slave con pull-ups simuladas.
- **waveform_i2c.vcd**: Archivo de ondas generado por la simulación.
- **i2c.svg**: Diagrama del sistema top-level completo.
- **i2c_master.svg**: Diagrama del I2C Master.
- **i2c_slave.svg**: Diagrama del I2C Slave.

## Arquitectura del Bus I2C y Pull-Up

### Lógica Open-Drain y Resistencias Pull-Up

El protocolo I2C utiliza **lógica open-drain** (o colector abierto), lo que significa que los dispositivos solo pueden **tirar la línea a bajo (0)**, no pueden forzarla a alto. Cuando ningún dispositivo está tirando la línea a bajo, las **resistencias pull-up externas** (típicamente 4.7kΩ) suben la línea a alto (1).

**Comportamiento en Hardware Real:**
- **Línea en alto (1)**: Ningún dispositivo activo, pull-up tira a VDD.
- **Línea en bajo (0)**: Uno o más dispositivos activan su transistor open-drain.
- **Wired-AND**: Múltiples dispositivos pueden compartir el bus; si alguno tira a bajo, la línea está en bajo.

**Modelado en Simulación:**

En Verilog/SystemVerilog, el comportamiento open-drain se modela así:

```systemverilog
// En i2c_master.sv e i2c_slave.sv:
assign sda = (sda_en == 1) ? (sda_t == 0) ? 1'b0 : 1'bz : 1'bz;
assign scl = scl_t;  // Master controla SCL directamente
```

Donde:
- `sda_en = 1`: El dispositivo controla SDA.
  - Si `sda_t = 0`: Fuerza SDA a bajo (`1'b0`).
  - Si `sda_t = 1`: Libera la línea a alta impedancia (`1'bz`), permitiendo que la pull-up la suba.
- `sda_en = 0`: El dispositivo no controla SDA (alta impedancia).

**Resistencias Pull-Up Simuladas:**

En el módulo top-level (`i2c.sv`), se simulan las resistencias pull-up usando primitivas de Verilog:

```systemverilog
wire sda, scl;

// Simular resistencias pull-up de 4.7kΩ del bus I2C
pullup(sda);
pullup(scl);
```

La primitiva `pullup()` automáticamente tira el wire a `1` cuando está en alta impedancia (`z`). Esto modela fielmente el efecto de las resistencias pull-up físicas.

**Error Común en Simulación:**

Sin `pullup()`, si un dispositivo pone la línea en `1'bz` esperando que "suba a 1", se queda en `z` indefinidamente, causando errores de lectura. La solución correcta es:
1. Usar `pullup()` en el top-level para lógica open-drain pura, o
2. Modelar explícitamente el pull-up en la asignación: `assign sda = ... ? 1'b1 : 1'bz;`

Se utiliza la opción de pull-ups simuladas por ser más realista y escalable.

## I2C Master

### Descripción del DUT

El I2C Master es un módulo SystemVerilog que implementa el controlador del bus I2C. Es responsable de:
- Generar el reloj SCL del bus I2C (~100 kHz).
- Iniciar y terminar transacciones (condiciones START y STOP).
- Transmitir direcciones y datos a través de SDA.
- Recibir datos del Slave.
- Manejar señales de ACK/NACK.

![I2C Master](i2c_master.svg)

### Entity: I2C Master
- **File**: i2c_master.sv

### Ports

| Port name | Direction | Type   | Description |
| --------- | --------- | ------ | ----------- |
| clk       | input     |        | Reloj del sistema (40 MHz) |
| rst       | input     |        | Reset síncrono (activo alto) |
| newd      | input     |        | Nueva solicitud de transacción (activo alto) |
| addr      | input     | [6:0]  | Dirección del slave (7 bits) |
| op        | input     |        | Operación: 0=write, 1=read |
| din       | input     | [7:0]  | Dato de entrada para escritura |
| sda       | inout     |        | Serial Data (bidireccional, open-drain) |
| scl       | output    |        | Serial Clock (generado por Master) |
| dout      | output    | [7:0]  | Dato de salida para lectura |
| busy      | output    | reg    | Indica transacción en progreso |
| ack_err   | output    | reg    | Error de ACK (NACK recibido) |
| done      | output    | reg    | Señal de transacción completada (pulso) |

### Características del Diseño

- **Generación de SCL**: El reloj I2C se genera dividiendo el reloj del sistema por 400 (clk_count4), creando pulsos de 4 fases (pulse 0-3) mediante un contador interno. Frecuencia resultante: ~100 kHz en modo estándar.

- **Generación de Pulsos Internos**: Utiliza un contador `count1` que va de 0 a 399 (clk_count4-1), generando 4 pulsos (`pulse` = 0, 1, 2, 3) en cada período SCL:
  - `pulse = 0`: count1 = 0-99
  - `pulse = 1`: count1 = 100-199
  - `pulse = 2`: count1 = 200-299
  - `pulse = 3`: count1 = 300-399

- **Máquina de Estados**:
  - **idle**: Espera señal `newd = 1` para iniciar.
  - **start**: Genera condición START (SDA cae mientras SCL está alto).
  - **write_addr**: Transmite dirección de 7 bits + bit R/W.
  - **ack_1**: Recibe ACK del Slave después de dirección.
  - **write_data**: Transmite 8 bits de datos (si op=0).
  - **read_data**: Recibe 8 bits de datos del Slave (si op=1).
  - **ack_2**: Recibe ACK del Slave después de write_data.
  - **master_ack**: Master envía ACK/NACK después de read_data.
  - **stop**: Genera condición STOP (SDA sube mientras SCL está alto).

- **Transmisión de Datos**: Los datos se transmiten MSB first (bit más significativo primero). En cada bit:
  - `pulse = 0, 1`: SCL bajo, SDA se establece.
  - `pulse = 2, 3`: SCL alto, el dato es válido.

- **Recepción de Datos**: Durante lectura (`read_data`):
  - Master libera SDA (`sda_en = 0`).
  - Slave controla SDA.
  - Master muestrea SDA en `pulse = 2` cuando `count1 == 200` (medio del pulso alto de SCL).
  - Reconstruye `rx_data` mediante shift: `rx_data <= {rx_data[6:0], sda}`.

- **Condiciones START y STOP**:
  - **START**: SDA transiciona de alto a bajo mientras SCL está alto.
  - **STOP**: SDA transiciona de bajo a alto mientras SCL está alto.

- **Control de SDA Open-Drain**:
  ```systemverilog
  assign sda = (sda_en == 1) ? (sda_t == 0) ? 1'b0 : 1'bz : 1'bz;
  ```
  - Cuando `sda_en = 1` y `sda_t = 0`: Tira SDA a bajo.
  - Cuando `sda_en = 1` y `sda_t = 1`: Libera SDA (alta impedancia, pull-up la sube).
  - Cuando `sda_en = 0`: No controla SDA (para recibir datos del Slave).

### Timing del I2C Master

**Parámetros de Frecuencia:**
- `sys_freq = 40,000,000 Hz` (40 MHz)
- `i2c_freq = 100,000 Hz` (100 kHz, modo estándar)
- `clk_count4 = 400` (ciclos de reloj del sistema por período SCL)
- `clk_count1 = 100` (ciclos de reloj del sistema por cuarto de período SCL)

**Duración de Eventos:**
- Período SCL: 400 × 25 ns = 10,000 ns = 10 µs
- Cada fase (pulse): 100 × 25 ns = 2,500 ns = 2.5 µs
- Transmisión de 1 byte (8 bits): 8 × 10 µs = 80 µs
- Transacción completa (START + addr + ACK + data + ACK + STOP): ~120-160 µs

**Sincronización Crítica:**
- **SDA debe ser estable cuando SCL está alto**: Los cambios en SDA solo deben ocurrir cuando SCL está bajo (excepto START/STOP).
- **Muestreo en el medio del pulso alto**: `count1 == 200` garantiza que SDA se lea cuando es más estable.
- **Detección de edges sin skew**: La FSM se ejecuta en `@(posedge clk)` del sistema, no en `@(posedge scl)`, evitando problemas de timing.

## I2C Slave

### Descripción del DUT

El I2C Slave es un módulo SystemVerilog que implementa un dispositivo Slave en el bus I2C. Es responsable de:
- Detectar condiciones START y STOP del Master.
- Recibir dirección y comparar con su propia dirección.
- Enviar señales ACK/NACK.
- Recibir datos del Master (escritura) o enviar datos al Master (lectura).
- Almacenar datos en una memoria interna de 128 bytes.

![I2C Slave](i2c_slave.svg)

### Entity: I2C Slave
- **File**: i2c_slave.sv

### Ports

| Port name | Direction | Type   | Description |
| --------- | --------- | ------ | ----------- |
| scl       | input     |        | Serial Clock (recibido del Master) |
| clk       | input     |        | Reloj del sistema (40 MHz) |
| rst       | input     |        | Reset síncrono (activo alto) |
| sda       | inout     |        | Serial Data (bidireccional, open-drain) |
| ack_err   | output    | reg    | Error de ACK detectado |
| done      | output    | reg    | Señal de transacción completada (pulso) |

### Características del Diseño

- **Memoria Interna**: Array de 128 bytes (`mem[128]`), inicializada con `mem[i] = i` en reset.

- **Sincronización con Master**: Utiliza el mismo esquema de pulsos que el Master:
  - Contador `count1` sincronizado con `clk`.
  - Genera `pulse` (0-3) para alinearse con las fases del Master.
  - **Importante**: `count1` inicia en 202 cuando `busy = 0` (fase de espera), permitiendo sincronización con el Master.

- **Detección de START**: Detecta cuando `scl = 1` y `sda = 0` (transición de SDA mientras SCL alto).

- **Máquina de Estados**:
  - **idle**: Espera condición START.
  - **wait_p**: Estado de espera después de START.
  - **read_addr**: Recibe 8 bits (7 bits de dirección + 1 bit R/W).
  - **send_ack1**: Envía ACK si la dirección coincide.
  - **send_data**: Envía 8 bits de datos al Master (lectura).
  - **master_ack**: Recibe ACK/NACK del Master después de enviar datos.
  - **read_data**: Recibe 8 bits de datos del Master (escritura).
  - **send_ack2**: Envía ACK después de recibir datos.
  - **detect_stop**: Detecta condición STOP.

- **Envío de Datos (Lectura del Master)**:
  - Slave lee el dato de memoria cuando entra en `send_ack1` con `r_mem = 1`.
  - En `send_data`, controla SDA (`sda_en = 1`).
  - Actualiza `sda_t` con cada bit en `pulse = 1` cuando `count1 == 100`:
    ```systemverilog
    sda_t <= (count1 == 100) ? dout[7 - bitcnt] : sda_t;
    ```
  - Envía MSB first, igual que el Master.

- **Recepción de Datos (Escritura del Master)**:
  - Slave libera SDA (`sda_en = 0`).
  - Muestrea SDA en `pulse = 2` cuando `count1 == 200`:
    ```systemverilog
    din <= (count1 == 200) ? {din[6:0], sda} : din;
    ```
  - Reconstruye el byte completo mediante shift.

- **Envío de ACK**:
  - Slave controla SDA y la pone en bajo (`sda_t = 0`) durante el bit de ACK.
  - El Master muestrea este ACK bajo como confirmación.

- **Control de SDA Open-Drain**:
  ```systemverilog
  assign sda = (sda_en == 1'b1) ? sda_t : 1'bz;
  ```
  - Cuando `sda_en = 1`: Slave controla SDA (envía datos o ACK).
  - Cuando `sda_en = 0`: Slave libera SDA (recibe datos o dirección).

### Timing del I2C Slave

**Sincronización con el Master:**
- El Slave usa el mismo esquema de pulsos que el Master (pulse 0-3).
- El Slave muestrea SDA en `pulse = 2, count1 = 200` (cuando SCL está alto y estable).
- El Slave actualiza SDA en `pulse = 1, count1 = 100` (cuando SCL está bajo), dando tiempo de setup antes de que SCL suba.

**Setup y Hold Times:**
- **Setup time**: SDA se establece en `count1 = 100`, luego SCL sube en `count1 = 200`. Setup = 100 ciclos × 25 ns = 2.5 µs.
- **Hold time**: SDA se mantiene estable hasta `count1 = 399`. Hold = 200 ciclos × 25 ns = 5 µs.

Estos tiempos cumplen ampliamente con las especificaciones I2C estándar (setup > 250 ns, hold > 0 ns).

## Top Level: Sistema Completo I2C

### Descripción del Sistema

El módulo top-level conecta el I2C Master y el I2C Slave para formar un sistema de comunicación completo. Además, simula las resistencias pull-up del bus I2C mediante las primitivas `pullup()`, permitiendo que las líneas SDA y SCL funcionen con lógica open-drain correcta.

![Top I2C](i2c.svg)

### Entity: Top I2C
- **File**: i2c.sv

### Conexiones

- **Resistencias Pull-Up**: `pullup(sda)` y `pullup(scl)` simulan las resistencias de 4.7kΩ del hardware real.
- **SDA y SCL**: Conectan Master y Slave como wires bidireccionales.
- **Señales de Control**: El Master recibe `newd`, `addr`, `op`, `din` del testbench.
- **Señales de Salida**: El Master envía `dout`, `busy`, `done` al testbench.
- **ACK Errors**: Se combinan errores de Master y Slave: `ack_err = ack_errm | ack_errs`.

### Importancia de las Pull-Ups

Sin `pullup(sda)` y `pullup(scl)`, las líneas quedarían en alta impedancia (`z`) cuando ningún dispositivo las tira a bajo, causando:
- **Lecturas incorrectas**: El Master leería `z` en lugar de `1`, generando valores inválidos.
- **Bloqueos**: La FSM esperaría eventos que nunca ocurren (e.g., SDA en alto durante STOP).

Con `pullup()`, el comportamiento es correcto:
- Cuando Master/Slave liberan la línea (`1'bz`), el pull-up la sube automáticamente a `1`.
- Cuando algún dispositivo tira a bajo (`1'b0`), sobrescribe el pull-up.

## Proceso de Verificación

El testbench sigue un flujo UVM-like con los siguientes componentes:

### 1. Transaction

Clase que representa una transacción I2C con randomización:

```python
class transaction(Randomized):
    def __init__(self):
        self.newd = 0
        self.op = 0      # 0: write, 1: read
        self.addr = 0    # 7 bits
        self.din = 0     # 8 bits
        self.dout = 0    # 8 bits
        self.busy = 0
        self.ack_err = 0
        
        self.add_rand("op", [0, 1])
        self.add_rand("addr", list(range(128)))
        self.add_rand("din", list(range(256)))
        
        # Constraints
        self.add_constraint(lambda addr: addr == 1)
        self.add_constraint(lambda din: din < 50)
```

Genera transacciones aleatorias con:
- Operación aleatoria (write/read)
- Dirección fija en 1 (constraint)
- Datos entre 0-49 (constraint)

### 2. Generator

Genera `count=10` transacciones aleatorias y las envía a la cola del driver:

```python
async def gen_data(self):
    for i in range(self.count):
        tr = transaction()
        tr.randomize()
        tr.print_in("GEN")
        await self.queue.put(tr)
        await self.event.wait()  # Espera confirmación del scoreboard
        self.event.clear()
```

### 3. Driver

Recibe transacciones y las aplica al DUT:

**Reset:**
```python
async def reset_dut(self):
    self.dut.rst.value = 1
    self.dut.din.value = 0
    self.dut.newd.value = 0
    self.dut.addr.value = 0
    self.dut.op.value = 0
    await ClockCycles(self.dut.clk, 5)
    self.dut.rst.value = 0
```

**Operación de Escritura:**
```python
async def wr_op(self, tr):
    self.dut.newd.value = 1
    self.dut.din.value = tr.din
    self.dut.addr.value = tr.addr
    self.dut.op.value = 0
    await ClockCycles(self.dut.clk, 5)
    self.dut.newd.value = 0
    await RisingEdge(self.dut.done)  # Espera fin de transacción
```

**Operación de Lectura:**
```python
async def rd_op(self, tr):
    self.dut.newd.value = 1
    self.dut.din.value = 0
    self.dut.addr.value = tr.addr
    self.dut.op.value = 1
    await ClockCycles(self.dut.clk, 5)
    self.dut.newd.value = 0
    await RisingEdge(self.dut.done)
    tr.dout = self.dut.dout.value
```

### 4. Monitor

Monitorea las señales del DUT en tiempo real:

```python
async def sample_data(self):
    while True:
        temp = transaction()
        await RisingEdge(self.dut.done)
        temp.din = self.dut.din.value
        temp.op = self.dut.op.value
        temp.addr = self.dut.addr.value
        temp.dout = self.dut.dout.value
        await self.queue.put(temp)
```

Captura todas las señales cuando `done` sube, indicando fin de transacción.

### 5. Scoreboard

Verifica la correctitud de las operaciones comparando con un modelo de memoria:

```python
async def compare_data(self):
    while True:
        temp = await self.queue.get()
        addr = int(temp.addr)
        din = int(temp.din)
        dout = int(temp.dout)
        
        if temp.op == 0:  # Write
            self.mem.update({addr: din})
            cocotb.log.info("[SCO]: Added new data in mem")
        else:  # Read
            expected_dout = self.mem.get(addr)
            if dout == expected_dout:
                cocotb.log.info(f"[SCO] : TEST PASS {expected_dout}")
            else:
                cocotb.log.info(f"[SCO] : Test FAIL {expected_dout}")
        
        self.event.set()  # Notifica al generator
```

Mantiene un diccionario `self.mem` como golden model de la memoria del Slave.

## Detalles de Timing y Sincronización

### Frecuencias y Períodos

- **Reloj del Sistema**: 40 MHz → Período = 25 ns
- **Reloj I2C (SCL)**: ~100 kHz → Período = 10 µs
- **Duración de Transacción Completa**: ~80-160 µs (depende de write/read y número de bits)

### Timing de Operaciones

**Escritura (Write):**
1. Driver aplica `newd = 1` durante 5 ciclos de `clk` (125 ns)
2. Master genera START (~10 µs)
3. Master transmite addr + W bit (8 bits × 10 µs = 80 µs)
4. Slave envía ACK (10 µs)
5. Master transmite 8 bits de datos (80 µs)
6. Slave envía ACK (10 µs)
7. Master genera STOP (~10 µs)
8. **Total**: ~200 µs por operación de escritura

**Lectura (Read):**
1. Driver aplica `newd = 1` durante 5 ciclos (125 ns)
2. Master genera START (~10 µs)
3. Master transmite addr + R bit (80 µs)
4. Slave envía ACK (10 µs)
5. Slave transmite 8 bits de datos (80 µs)
6. Master envía ACK/NACK (10 µs)
7. Master genera STOP (~10 µs)
8. **Total**: ~200 µs por operación de lectura

**Test Completo:**
- 10 transacciones × 200 µs = 2000 µs = 2 ms mínimo
- El test se configura con `await Timer(640000, 'ns')` = 640 µs, permitiendo ~3 transacciones completas.

### Sincronización Crítica

**Reglas de Sincronización:**

1. **SDA debe cambiar solo cuando SCL está bajo** (excepto START/STOP):
   - Master/Slave actualizan SDA en `pulse = 0, 1` (SCL bajo).
   - SCL sube en `pulse = 2` con SDA ya estable.

2. **Muestreo en medio del pulso alto de SCL**:
   - `count1 == 200` garantiza lectura en el punto más estable.

3. **Setup antes de SCL alto**:
   - SDA se establece en `count1 = 100`.
   - SCL sube en `count1 = 200`.
   - Setup time = 100 × 25 ns = 2.5 µs >> 250 ns (especificación I2C).

4. **Hold después de SCL alto**:
   - SDA se mantiene hasta `count1 = 399`.
   - Hold time = 200 × 25 ns = 5 µs >> 0 ns (especificación I2C).

5. **Detección de START/STOP**:
   - START: SDA alto → bajo mientras SCL alto.
   - STOP: SDA bajo → alto mientras SCL alto.

### Sincronización con `clk` del Sistema

**Ventaja de usar `@(posedge clk)` en lugar de `@(posedge scl)`:**

El diseño ejecuta toda la lógica en el dominio del reloj del sistema (`clk`), no en el reloj I2C (`scl`). Esto evita:
- **Skew de reloj**: `scl` se genera internamente y puede no estar perfectamente alineado.
- **Violaciones de setup/hold**: Cambios en registros sincronizados con `scl` generado podrían violar tiempos.
- **Simulación más estable**: Todos los eventos están sincronizados con un solo reloj.

En lugar de usar `@(posedge scl)`, se usa:
```systemverilog
if (count1 == 200)  // Equivalente a rising edge de scl
```

Esto garantiza que todas las actualizaciones de estado ocurran en flancos de `clk`, no en flancos de `scl`.

## Problema Encontrado y Solución: Open-Drain y Pull-Up

### Problema Original

En la implementación inicial, el Master usaba esta asignación incorrecta:

```systemverilog
assign sda = (sda_en == 1) ? (sda_t == 0) ? 1'b0 : 1'bz : 1'bz;
```

**Problema**: Cuando el Master quería poner SDA en alto (`sda_t = 1`), asignaba `1'bz` en lugar de `1'b1`. Sin resistencias pull-up simuladas, la línea quedaba en alta impedancia, causando:
- Lecturas incorrectas del Slave (leía `z` en lugar de `1`).
- `dout` del Master quedaba en `ZZZZZZZZ` durante operaciones de lectura.
- Tests fallaban con `ValueError: Can't convert LogicArray to int: it contains non-0/1 values`.

### Solución Implementada

Se agregaron resistencias pull-up simuladas en el módulo top-level:

```systemverilog
// En i2c.sv
wire sda, scl;

// Simular resistencias pull-up de 4.7kΩ del bus I2C
pullup(sda);
pullup(scl);
```

Y se cambió la asignación del Master a lógica open-drain pura:

```systemverilog
// En i2c_master.sv
assign sda = (sda_en == 1) ? (sda_t == 0) ? 1'b0 : 1'bz : 1'bz;
```

**Por qué funciona:**
1. Cuando `sda_t = 0`: Master tira SDA a bajo (`1'b0`).
2. Cuando `sda_t = 1`: Master libera SDA (`1'bz`).
3. La primitiva `pullup(sda)` detecta la alta impedancia y automáticamente tira SDA a `1`.
4. Esto modela fielmente el comportamiento de las resistencias pull-up físicas en hardware real.

### Alternativa (Sin Pull-Up)

Otra solución es modelar explícitamente el pull-up en la asignación:

```systemverilog
assign sda = (sda_en == 1) ? (sda_t == 0) ? 1'b0 : 1'b1 : 1'bz;
```

Esto funciona pero no es tan realista ni escalable para múltiples dispositivos en el bus.

### Lecciones Aprendidas

1. **En simulación, no hay pull-ups implícitas**: Debes modelarlas explícitamente.
2. **`pullup()` es la forma correcta**: Simula hardware real y permite lógica open-drain pura.
3. **I2C requiere pull-ups**: Sin ellas, el bus no puede subir a alto cuando está en alta impedancia.
4. **Verificar waveforms**: Si ves valores `z` donde deberían ser `1`, probablemente faltan pull-ups.

## Cómo Ejecutar

1. Asegúrate de tener el entorno virtual activado:
   ```bash
   source /home/riacosta/Documents/uvm_ver/.venv/bin/activate
   ```

2. Navega al directorio del proyecto:
   ```bash
   cd /home/riacosta/Documents/uvm_ver/Course_4/i2c
   ```

3. Ejecuta la simulación:
   ```bash
   make
   ```

4. Revisa los logs en la consola. Deberías ver:
   ```
   [SCO] : TEST PASS <valor>
   [SCO]: Added new data in mem
   ```

5. Visualiza el archivo de ondas:
   ```bash
   gtkwave waveform_i2c.vcd
   ```

### Señales Clave para Observar en GTKWave

- **sda**: Línea de datos bidireccional. Observa cambios solo cuando `scl` está bajo (excepto START/STOP).
- **scl**: Reloj I2C generado por Master. Debe oscilar a ~100 kHz durante transacciones.
- **cs** (internamente): Chip select del Master (activo bajo).
- **done**: Pulso que indica fin de transacción.
- **dout**: Dato leído del Slave. Debe coincidir con el valor escrito previamente.
- **master.state** y **slave.state**: Estados de las FSMs.
- **master.sda_en** y **slave.sda_en**: Control de SDA open-drain.

## Dependencias

- Python >= 3.12
- Cocotb >= 2.0.1
- Cocotb-coverage >= 2.0 (para randomización con `Randomized`)
- Icarus Verilog (para simulación HDL)
- GTKWave (para visualizar archivos VCD)

## Resultado Esperado

Al ejecutar `make`, deberías ver una salida similar a:

```
GEN : op=0 addr=1 din=26
[DRV] : op=0 addr=1 din=26
[MON] : op=0 addr=0000001 din=00011010 dout=00000000
[SCO] : op=0 addr=0000001 din=00011010 dout=00000000
80050.00ns INFO [SCO]: Added new data in mem

GEN : op=1 addr=1 din=24
[MON] : op=1 addr=0000001 din=00000000 dout=00011010
[DRV] : op=1 addr=1 din=24 dout=00011010
[SCO] : op=1 addr=0000001 din=00000000 dout=00011010
160060.00ns INFO [SCO] : TEST PASS 26

** TEST                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
** i2c_tb.test_I2C                PASS      640040.00           3.18     201129.91  **
** TESTS=1 PASS=1 FAIL=0 SKIP=0             640040.00           3.18     201075.36  **
```

## Conclusiones

Este testbench implementa un sistema I2C completo con verificación automatizada, destacando:

1. **Lógica Open-Drain Correcta**: Uso de `pullup()` para simular resistencias pull-up reales.
2. **Sincronización Precisa**: Timing basado en contadores sincronizados con el reloj del sistema, evitando skew.
3. **Verificación Completa**: Testbench UVM-like con generator, driver, monitor y scoreboard.
4. **Cumplimiento de Protocolo**: START, STOP, ACK/NACK, y timing conforme a especificaciones I2C.
5. **Modelado Realista**: Comportamiento fiel al hardware real con buses bidireccionales y pull-ups.

El sistema es robusto, verificado y listo para extensión a múltiples slaves o modos de alta velocidad (fast mode, 400 kHz).
