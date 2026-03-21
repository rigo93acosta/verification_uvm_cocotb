// SPI Slave - Basic Implementation
// Supports CPOL=0, CPHA=0 (Mode 0)
// Has internal register/memory that can be read/written

module spi_slave #(
    parameter DATA_WIDTH = 8,
    parameter SLAVE_ID = 0  // Unique ID for each slave
)(
    input  logic clk,
    input  logic rst_n,
    
    // SPI interface
    input  logic spi_sclk,
    input  logic spi_mosi,
    output logic spi_miso,
    input  logic spi_cs_n,
    
    // Status outputs (for verification)
    output logic [DATA_WIDTH-1:0] last_rx_data,
    output logic                  rx_done,
    output logic [7:0]            transaction_count
);

    // Internal registers
    logic [DATA_WIDTH-1:0] shift_reg_rx;
    logic [DATA_WIDTH-1:0] shift_reg_tx;
    logic [DATA_WIDTH-1:0] internal_reg;
    logic [$clog2(DATA_WIDTH)-1:0] bit_counter;
    logic spi_sclk_d, spi_sclk_rising, spi_sclk_falling;
    logic spi_cs_n_d;
    logic transfer_active;
    
    // Edge detection for SCLK
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            spi_sclk_d <= 0;
        end else begin
            spi_sclk_d <= spi_sclk;
        end
    end
    
    assign spi_sclk_rising = spi_sclk && !spi_sclk_d;
    assign spi_sclk_falling = !spi_sclk && spi_sclk_d;
    
    // CS edge detection
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            spi_cs_n_d <= 1;
        end else begin
            spi_cs_n_d <= spi_cs_n;
        end
    end
    
    // Transfer active flag
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            transfer_active <= 0;
        end else begin
            if (!spi_cs_n && spi_cs_n_d) begin
                // CS falling edge - start transfer
                transfer_active <= 1;
            end else if (spi_cs_n && !spi_cs_n_d) begin
                // CS rising edge - end transfer
                transfer_active <= 0;
            end
        end
    end
    
    // Bit counter
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            bit_counter <= 0;
        end else begin
            if (!spi_cs_n && spi_cs_n_d) begin
                bit_counter <= 0;
            end else if (transfer_active && spi_sclk_rising) begin
                bit_counter <= bit_counter + 1;
            end
        end
    end
    
    // RX shift register (sample on rising edge)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg_rx <= 0;
        end else if (transfer_active && spi_sclk_rising) begin
            shift_reg_rx <= {shift_reg_rx[DATA_WIDTH-2:0], spi_mosi};
        end
    end
    
    // TX shift register (update on falling edge)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg_tx <= 0;
        end else begin
            if (!spi_cs_n && spi_cs_n_d) begin
                // Load TX data at start of transfer
                shift_reg_tx <= internal_reg;
            end else if (transfer_active && spi_sclk_falling) begin
                shift_reg_tx <= {shift_reg_tx[DATA_WIDTH-2:0], 1'b0};
            end
        end
    end
    
    // MISO output
    assign spi_miso = !spi_cs_n ? shift_reg_tx[DATA_WIDTH-1] : 1'bz;
    
    // Internal register (updates when full byte received)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            internal_reg <= SLAVE_ID;  // Initialize with slave ID
        end else if (transfer_active && bit_counter == DATA_WIDTH-1 && spi_sclk_rising) begin
            // Store received data
            internal_reg <= {shift_reg_rx[DATA_WIDTH-2:0], spi_mosi};
        end
    end
    
    // Output last received data
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            last_rx_data <= 0;
            rx_done <= 0;
        end else begin
            if (spi_cs_n && !spi_cs_n_d) begin
                // CS rising edge - transfer complete
                last_rx_data <= internal_reg;
                rx_done <= 1;
            end else begin
                rx_done <= 0;
            end
        end
    end
    
    // Transaction counter
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            transaction_count <= 0;
        end else if (rx_done) begin
            transaction_count <= transaction_count + 1;
        end
    end

endmodule
