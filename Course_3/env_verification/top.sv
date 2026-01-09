module top(
    input  [3:0]  a,
    input  [3:0]  b,
    output [3:0]  y,
    input clk
  );

  reg [1:0] count = 0;
  reg [3:0] y_t = 0;

  always@(posedge clk)
  begin
    if (count == 1)
    begin
      count <=         0;
      y_t   <=   y_t + 1;
    end
    else
    begin
      count <= count + 1;
    end
  end

  assign y = y_t;

  initial
  begin
    $dumpfile("env_ver.vcd");
    $dumpvars(1,top);
  end

endmodule
