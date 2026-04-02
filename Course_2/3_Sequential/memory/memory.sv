module top(
    input rst,clk,
    input wr,
    input [7:0] din,
    input [3:0] addr,
    output [7:0] dout
  );

  reg [7:0] mem [16];
  reg [7:0] temp = 8'h00;

  always@(posedge clk)
  begin
    if     (rst == 1'b1)
    begin
      for (int i =0; i < 16; i++)
      begin
        mem[i] <= 0;
      end
      temp      <= 8'h0;
    end
    else if (wr == 1'b1)
    begin
      mem[addr] <= din;
    end
    else
      temp      <= mem[addr];
  end


  assign dout = temp;



  initial
  begin
    $dumpfile("memory.vcd");
    $dumpvars(1,top);
  end


endmodule
