module SPI_SLAVE (
    input         sclk,
    input           cs,
    input         mosi,
    output [11:0] dout,
    output reg     done
  );

  typedef enum bit {detect_start = 1'b0, read_data = 1'b1} state_type;
  state_type state = detect_start;

  reg [11:0] temp = 12'h000;
  int count = 0;

  always@(posedge sclk or posedge cs)
  begin
    if (cs == 1'b1)
    begin
      state <= detect_start;
      count <= 0;
      done  <= 1'b1;
    end
    else
    begin
      done <= 1'b0;
      case(state)
        detect_start:
        begin
          if(cs == 1'b0)
            state <= read_data;
          else
            state <= detect_start;
        end

        read_data :
        begin
          if(count < 11)
          begin
            count <= count + 1;
            temp  <= { temp[10:0], mosi};
          end
          else
          begin
            temp  <= { temp[10:0], mosi};
            count <= 0;
            state <= detect_start;
          end

        end

      endcase
    end
  end
  assign dout = temp;

endmodule
