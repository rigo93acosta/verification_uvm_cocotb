module SPI (
    input        clk,
    input        rst,
    input       newd,
    input [11:0] din,
    output reg  sclk,
    output reg  mosi,
    output reg    cs
  );

  typedef enum bit {
            idle   = 2'b00,
            enable = 2'b01,
            send   = 2'b10,
            comp   = 2'b11
          } state_type;

  state_type state = idle;

  int countc = 0;
  int count  = 0;

  // generation of sclk
  always @(posedge clk)
  begin : GEN_SCLK
    if (rst == 1'b1)
    begin
      countc <=    0;
      sclk   <= 1'b0;
    end
    else
    begin
      if (countc < 10)
        countc <= countc + 1;
      else
      begin
        countc <=     0;
        sclk   <= ~sclk;
      end
    end
  end

  // state machine
  reg [11:0] temp;
  always @(posedge sclk)
  begin : FSM_SPI
    if (rst == 1'b1)
    begin
      cs   <=  1'b1;
      mosi <=  1'b0;
      temp <= 12'h0;
    end
    else
    begin
      case (state)
        idle :
        begin
          if(newd == 1'b1)
          begin
            state <= send;
            temp  <=  din;
            cs    <= 1'b0;
          end
          else
          begin
            state <=    idle;
            temp  <= 12'h000;
          end
        end
        send :
        begin
          if (count <= 11)
          begin
            mosi  <= temp[count];
            count <=   count + 1;
          end
          else
          begin
            count <=    0;
            state <= idle;
            cs    <= 1'b1;
            mosi  <= 1'b0;
          end
        end
        default:
          state <= idle;
      endcase
    end
  end

  initial begin
    $dumpfile("waveform_spi.vcd");
    $dumpvars(1, SPI); 
  end

endmodule
