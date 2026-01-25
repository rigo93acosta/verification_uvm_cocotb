`include "uart_tx.sv"
`include "uart_rx.sv"

module UART
  #(
     parameter clk_freq = 1000000,
     parameter baud_rate = 9600
   )(
     input            clk,
     input            rst,
     input             rx,
     input  [7:0]   dintx,
     input           newd,
     output            tx,
     output [7:0]  doutrx,
     output        donetx,
     output        donerx
   );

  UART_TX
    #(
      .clk_freq (clk_freq),
      .baud_rate(baud_rate)
    ) uart_tx_inst (
      .clk    (clk),
      .rst    (rst),
      .newd   (newd),
      .tx_data(dintx),
      .tx     (tx),
      .donetx (donetx)
    );

  UART_RX
    #(
      .clk_freq (clk_freq),
      .baud_rate(baud_rate)
    ) uart_rx_inst (
      .clk    (clk),
      .rst    (rst),
      .rx     (rx),
      .rx_data(doutrx),
      .done   (donerx)
    );

  initial
  begin
    $dumpfile("waveform_uart.vcd");
    $dumpvars(1,UART);
  end




endmodule
