// filter.v
/*
    Módulo Verilog para un filtro FIR simple con detección de overflow.
    Este módulo implementa un filtro FIR de orden 2 y tiene como objetivo
    de cobertura detectar condiciones de overflow en la salida.
*/

module filter (
    input                         clk,
    input                         rst,
    input      signed [7:0]   data_in,
    input      signed [7:0]    coeff0,
    input      signed [7:0]    coeff1,
    input      signed [7:0]    coeff2,
    output reg signed [15:0] data_out,
    output reg      overflow_detected
  );
  reg signed [7:0] z1, z2;

  always @(posedge clk or posedge rst)
  begin
    if (rst)
    begin
      z1 <= 0;
      z2 <= 0;
      data_out <= 0;
      overflow_detected <= 0;
    end
    else
    begin
      z1 <= data_in;
      z2 <= z1;
      // Cálculo del filtro
      data_out <= (data_in * coeff0) + (z1 * coeff1) + (z2 * coeff2);
      // Objetivo de cobertura: detectar si la suma excede un umbral alto
      if (data_out > 16000 || data_out < -16000)
        overflow_detected <= 1;
      else
        overflow_detected <= 0;
    end
  end
endmodule
