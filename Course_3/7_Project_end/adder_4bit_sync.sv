module adder_4bit_sync (
    input [3:0] a,
    input [3:0] b,
    input clk,
    output [4:0] y
);

  reg [4:0] y_t = 0;

  always @(posedge clk) begin
    y_t <= a + b;
  end

  assign y = y_t;

endmodule
