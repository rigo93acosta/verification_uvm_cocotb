module top(
    input      rst,clk,
    input      din,
    output reg dout
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
    $dumpfile("d_ff.vcd");
    $dumpvars(1,top);
  end


endmodule
