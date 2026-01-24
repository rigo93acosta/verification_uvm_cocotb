module dff (
    input       clk,
    input       rst,
    input       din,
    output reg  dout
  );

  always@(posedge clk)
  begin
    if(rst == 1'b1)
      dout <= 1'b0;
    else
      dout <= din;
  end


  initial
  begin
    $dumpfile("dump.vcd");
    $dumpvars(1, dff);
  end


endmodule
