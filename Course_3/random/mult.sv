module mul
  (
    input  [3:0] a,b,
    output [7:0] y
  );

  assign y = a * b;


  initial
  begin
    $dumpfile("mult.vcd");
    $dumpvars;
  end

endmodule
