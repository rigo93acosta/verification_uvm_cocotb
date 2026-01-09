`timescale 1ns / 1ps

module mult
  (
    input  [3:0] a,
    input  [3:0] b,
    output [7:0] y
  );

  assign y = a * b;


  initial
  begin
    $dumpfile("mult.vcd");
    $dumpvars;
  end

endmodule
