module SPI (
    input        clk,
    input        rst,
    input       newd,
    input [11:0] din,
    output reg  sclk,
    output reg  mosi,
    output reg    cs
  );

  typedef enum bit[1:0] {
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
    else if (cs == 1'b0) // only toggle sclk when CS is low
    begin
      if (countc < 10)
        countc <= countc + 1;
      else
      begin
        countc <=     0;
        sclk   <= ~sclk;
      end
    end
    else
    begin
      countc <=    0;
      sclk   <= 1'b0;
    end
  end

  // state machine
  reg [11:0] temp;
  wire sclk_edge = (countc == 10 && sclk == 1'b1);
  // Warning skew: sclk_edge must be used with care to avoid timing issues
  always @(posedge clk)
  begin : FSM_SPI
    if (rst == 1'b1)
    begin
      cs    <=  1'b1;
      mosi  <=  1'b0;
      temp  <= 12'h0;
      count <=     0;
      state <=  idle;
    end
    else
    begin
      case (state)
        idle :
        begin
          cs <= 1'b1; // Aseguramos que CS sea 1 en reposo
          if(newd == 1'b1)
          begin
            state <= send;
            temp  <=  din;
            cs    <= 1'b0; // activate chip select
            count <=    0;
          end
        end
        send :
        begin
          if (sclk_edge)
          begin
            if (count <= 11)
            begin
              mosi  <= temp[11 - count]; // MSB first
              count <=   count + 1;
            end
            else
            begin
              state <= idle;
              cs    <= 1'b1;
              mosi  <= 1'b0;
            end
          end
        end
        default:
          state <= idle;
      endcase
    end
  end

  initial
  begin
    $dumpfile("waveform_spi.vcd");
    $dumpvars(1, SPI);
  end

endmodule
