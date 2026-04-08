`include "spi_my.sv"
`include "spi_slave.sv"

module TOP (
    input          clk,
    input          rst,
    input         newd,
    input  [11:0]  din,
    output [11:0] dout,
    output        done
  );

  wire        sclk;
  wire        mosi;
  wire         cs;

  SPI spi_master (
        .clk   (clk),
        .rst   (rst),
        .newd (newd),
        .din   (din),
        .sclk (sclk),
        .mosi (mosi),
        .cs     (cs)
      );

  SPI_SLAVE spi_slave_inst (
              .sclk (sclk),
              .cs     (cs),
              .mosi (mosi),
              .dout (dout),
              .done (done)
            );


endmodule
