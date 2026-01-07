module top(input clk1,clk2,
             input [3:0] a,b,
             output reg [4:0] y
            );


  always@(posedge clk1)
  begin
    y <= a + b;
  end

  initial
  begin
    $dumpfile("dump.vcd");
    $dumpvars(1,top);
  end


endmodule
