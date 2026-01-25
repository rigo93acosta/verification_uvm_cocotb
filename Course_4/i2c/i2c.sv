`include "i2c_slave.sv"
`include "i2c_master.sv"

module I2C (
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

  i2c_master master (
               .clk      (clk      ),
               .rst      (rst      ),
               .newd     (newd     ),
               .addr     (addr     ),
               .op       (op       ),
               .sda      (sda      ),
               .scl      (scl      ),
               .din      (din      ),
               .dout     (dout     ),
               .busy     (busy     ),
               .ack_err  (ack_errm ),
               .done     (done     )
             );

  i2c_slave slave (
              .scl      (scl      ),
              .clk      (clk      ),
              .rst      (rst      ),
              .sda      (sda      ),
              .ack_err  (ack_errs )
            );

  assign ack_err = ack_errs | ack_errm;

  initial
  begin
    $dumpfile("waveform_i2c.vcd");
    $dumpvars(1,i2c_top);
  end


endmodule
