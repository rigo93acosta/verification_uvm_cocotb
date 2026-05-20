`timescale 1ns / 1ps

module adder (
    input rst
);

  reg clk = 0;

  always begin
    #10;
    clk = ~clk;
  end

  initial begin
    $dumpfile("adder.vcd");
    $dumpvars(1, adder);
  end

endmodule
