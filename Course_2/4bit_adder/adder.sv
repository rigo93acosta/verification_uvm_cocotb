`timescale 1ns/1ps

module adder(
    input      [3:0] a,b,
    output reg [4:0] y
  );

  always@(*)
  begin
    y = a + b;
  end

  initial
  begin
    $dumpfile("dump.vcd");
    $dumpvars(1,adder);
  end

endmodule
