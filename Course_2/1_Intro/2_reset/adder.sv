`timescale 1ns/1ps

module adder (
    input rst
  );

  reg clk = 0;

  always #5 clk = ~clk;

  initial
  begin
    $dumpfile("adder.vcd");
    $dumpvars(1, adder);
  end

endmodule
