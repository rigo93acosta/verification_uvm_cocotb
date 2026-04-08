module top (
    input clk,
    input [3:0] a,
    b,
    output [4:0] y
);
  reg [4:0] y_t = 0;


  always @(posedge clk) begin
    y_t <= a + b;
  end

  assign y = y_t;

endmodule
