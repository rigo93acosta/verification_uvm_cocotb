`timescale 1ns/1ps

module sum (
    input [3:0] a, b,
    output [4:0] s
  );

  assign s = a + b;

  initial begin
    $dumpfile("dump.vcd");
    $dumpvars(1,sum);
    // #500;
    // $finish;
  end

endmodule
