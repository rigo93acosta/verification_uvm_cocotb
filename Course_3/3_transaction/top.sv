module top(
  input clk
  );

  initial
  begin
    $dumpfile("transaction.vcd");
    $dumpvars(1,top);
  end


endmodule
