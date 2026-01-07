module top (
    input clk,
    input clk1,
    input clk2,
    input clk3
);

initial begin
    $dumpfile("clocks.vcd");
    $dumpvars(1, top);
end
    
endmodule