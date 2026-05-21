module mux (
    input [7:0] a,
    input [7:0] b,
    input [7:0] c,
    input [7:0] d,
    input [1:0] sel,
    output reg [7:0] dout
);

  always @(*) begin
    case (sel)
      2'b00:   dout = a;
      2'b01:   dout = b;
      2'b10:   dout = c;
      2'b11:   dout = d;
      default: dout = 8'h00;
    endcase
  end

endmodule
