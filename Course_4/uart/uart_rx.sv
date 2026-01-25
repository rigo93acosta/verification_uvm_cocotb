module UART_RX
  #(
     parameter clk_freq = 1000000,
     parameter baud_rate = 9600
   ) (
     input                  clk,
     input                  rst,
     input                   rx,
     output reg [7:0]   rx_data,
     output reg            done
   );

  localparam clkcount = clk_freq / baud_rate;

  integer count  = 0;
  integer counts = 0;

  reg     uclk   = 0;

  enum bit [1:0] {
         idle       =2'b00,
         start      =2'b01,
         transfer   =2'b10,
         done       =2'b11
       } state;

  always@(posedge clk)
  begin: uart_clock
    if(count < clkcount/2)
      count <= count + 1;
    else
    begin
      count <= 0;
      uclk <= ~uclk;
    end
  end

  always @(posedge uclk)
  begin: uart_rx_fsm
    if(rst)
    begin
      rx_data <= 8'b0;
      counts  <=    0;
      done    <= 1'b0;
    end
    else
    begin
      case (state)
        idle:
        begin
          rx_data <= 8'h0;
          counts <=    0;
          done    <= 1'b0;
          if(rx == 1'b0) // start bit detected
            state <= start;
          else
            state <= idle;
        end
        start:
        begin
          if(counts <= 7) // middle of start bit
          begin
            counts <= counts + 1;
            rx_data <= {rx, rx_data[7:1]};
          end
          else
          begin
            counts <=    0;
            done   <= 1'b1;
            state  <= idle;
          end
        end
        default:
          state <= idle;
      endcase
    end
  end

endmodule
