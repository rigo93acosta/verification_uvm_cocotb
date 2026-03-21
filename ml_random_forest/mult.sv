// 8-bit Unsigned Multiplier
// Simple combinational multiplier for ML verification testing

module mult (
    input  logic [7:0] a,
    input  logic [7:0] b,
    output logic [15:0] product
);

    // Combinational multiplication
    assign product = a * b;

endmodule
