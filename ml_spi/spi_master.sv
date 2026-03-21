// SPI Master - Basic Implementation
// Supports CPOL=0, CPHA=0 (Mode 0)
// Configurable data width

module spi_master #(
    parameter DATA_WIDTH = 8,
    parameter CLK_DIV = 4  // SPI clock divider
)(
    input  logic clk,
    input  logic rst_n,
    
    // Control interface
    input  logic [DATA_WIDTH-1:0] tx_data,
    input  logic                  tx_valid,
    output logic                  tx_ready,
    
    output logic [DATA_WIDTH-1:0] rx_data,
    output logic                  rx_valid,
    
    input  logic [1:0]            slave_select, // Select slave 0, 1, or 2
    
    // SPI interface
    output logic                  spi_sclk,
    output logic                  spi_mosi,
    input  logic                  spi_miso,
    output logic [1:0]            spi_cs_n     // 2 chip selects
);

    // FSM states
    typedef enum logic [1:0] {
        IDLE,
        TRANSFER,
        DONE
    } state_t;
    
    state_t state, next_state;
    
    // Internal registers
    logic [DATA_WIDTH-1:0] shift_reg;
    logic [DATA_WIDTH-1:0] rx_shift_reg;
    logic [$clog2(DATA_WIDTH)-1:0] bit_counter;
    logic [$clog2(CLK_DIV)-1:0] clk_counter;
    logic sclk_enable;
    logic sclk_int;
    
    // Clock divider for SPI clock
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            clk_counter <= 0;
            sclk_int <= 0;
        end else if (sclk_enable) begin
            if (clk_counter == CLK_DIV-1) begin
                clk_counter <= 0;
                sclk_int <= ~sclk_int;
            end else begin
                clk_counter <= clk_counter + 1;
            end
        end else begin
            clk_counter <= 0;
            sclk_int <= 0;
        end
    end
    
    // FSM - State register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end
    
    // FSM - Next state logic
    always_comb begin
        next_state = state;
        case (state)
            IDLE: begin
                if (tx_valid)
                    next_state = TRANSFER;
            end
            
            TRANSFER: begin
                if (bit_counter == DATA_WIDTH-1 && sclk_int && clk_counter == CLK_DIV-1)
                    next_state = DONE;
            end
            
            DONE: begin
                next_state = IDLE;
            end
        endcase
    end
    
    // Bit counter
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            bit_counter <= 0;
        end else if (state == TRANSFER) begin
            if (sclk_int && clk_counter == CLK_DIV-1) begin
                bit_counter <= bit_counter + 1;
            end
        end else begin
            bit_counter <= 0;
        end
    end
    
    // Shift register for TX
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg <= 0;
        end else if (state == IDLE && tx_valid) begin
            shift_reg <= tx_data;
        end else if (state == TRANSFER && ~sclk_int && clk_counter == CLK_DIV-1) begin
            shift_reg <= {shift_reg[DATA_WIDTH-2:0], 1'b0};
        end
    end
    
    // Shift register for RX
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_shift_reg <= 0;
        end else if (state == TRANSFER && sclk_int && clk_counter == CLK_DIV/2) begin
            rx_shift_reg <= {rx_shift_reg[DATA_WIDTH-2:0], spi_miso};
        end
    end
    
    // Output assignments
    assign tx_ready = (state == IDLE);
    assign sclk_enable = (state == TRANSFER);
    assign spi_sclk = sclk_int && sclk_enable;
    assign spi_mosi = shift_reg[DATA_WIDTH-1];
    
    // Chip select logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            spi_cs_n <= 2'b11;
        end else begin
            if (state == IDLE) begin
                spi_cs_n <= 2'b11;
            end else if (state == TRANSFER || state == DONE) begin
                case (slave_select)
                    2'b00: spi_cs_n <= 2'b10;  // Select slave 0
                    2'b01: spi_cs_n <= 2'b01;  // Select slave 1
                    default: spi_cs_n <= 2'b11;
                endcase
            end
        end
    end
    
    // RX valid and data
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_valid <= 0;
            rx_data <= 0;
        end else if (state == DONE) begin
            rx_valid <= 1;
            rx_data <= rx_shift_reg;
        end else begin
            rx_valid <= 0;
        end
    end

endmodule
