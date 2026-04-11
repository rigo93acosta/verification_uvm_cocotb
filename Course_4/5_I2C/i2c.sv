`include "i2c_s.sv"
`include "i2c_m.sv"

module i2c (
    input            clk,
    input            rst,
    input           newd,
    input             op,
    input  [6:0]    addr,
    input  [7:0]     din,
    output [7:0]    dout,
    output          busy,
    output       ack_err,
    output          done
  );

  wire sda, scl;
  wire ack_errm, ack_errs;

  // Simular resistencias pull-up de 4.7kΩ del bus I2C
  pullup(sda);
  pullup(scl);

  i2c_m master (
    .clk     (clk),
    .rst     (rst),
    .newd    (newd),
    .addr    (addr),
    .op      (op),
    .sda     (sda),
    .scl     (scl),
    .din     (din),
    .dout    (dout),
    .busy    (busy),
    .ack_err (ack_errm),
    .done    (done)
  );

  i2c_s slave (
    .scl     (scl),
    .clk     (clk),
    .rst     (rst),
    .sda     (sda),
    .ack_err (ack_errs)
  );

  assign ack_err = ack_errm | ack_errs;

endmodule
