// SPI System Top Level
// 1 Master + 2 Slaves

module spi_top #(
    parameter DATA_WIDTH = 8,
    parameter CLK_DIV = 4
)(
    input  logic clk,
    input  logic rst_n,
    
    // Master control interface
    input  logic [DATA_WIDTH-1:0] tx_data,
    input  logic                  tx_valid,
    output logic                  tx_ready,
    
    output logic [DATA_WIDTH-1:0] rx_data,
    output logic                  rx_valid,
    
    input  logic [1:0]            slave_select,
    
    // Slave status outputs (for verification)
    output logic [DATA_WIDTH-1:0] slave0_rx_data,
    output logic                  slave0_rx_done,
    output logic [7:0]            slave0_tx_count,
    
    output logic [DATA_WIDTH-1:0] slave1_rx_data,
    output logic                  slave1_rx_done,
    output logic [7:0]            slave1_tx_count
);

    // SPI bus signals
    logic spi_sclk;
    logic spi_mosi;
    logic spi_miso;
    logic [1:0] spi_cs_n;
    
    // MISO signals from each slave
    logic spi_miso_slave0;
    logic spi_miso_slave1;
    
    // MISO multiplexing (only active slave drives)
    assign spi_miso = (!spi_cs_n[0]) ? spi_miso_slave0 :
                     (!spi_cs_n[1]) ? spi_miso_slave1 :
                     1'bz;
    
    // SPI Master instantiation
    spi_master #(
        .DATA_WIDTH(DATA_WIDTH),
        .CLK_DIV(CLK_DIV)
    ) master_inst (
        .clk(clk),
        .rst_n(rst_n),
        .tx_data(tx_data),
        .tx_valid(tx_valid),
        .tx_ready(tx_ready),
        .rx_data(rx_data),
        .rx_valid(rx_valid),
        .slave_select(slave_select),
        .spi_sclk(spi_sclk),
        .spi_mosi(spi_mosi),
        .spi_miso(spi_miso),
        .spi_cs_n(spi_cs_n)
    );
    
    // SPI Slave 0 instantiation
    spi_slave #(
        .DATA_WIDTH(DATA_WIDTH),
        .SLAVE_ID(8'hA0)  // Slave 0 ID
    ) slave0_inst (
        .clk(clk),
        .rst_n(rst_n),
        .spi_sclk(spi_sclk),
        .spi_mosi(spi_mosi),
        .spi_miso(spi_miso_slave0),
        .spi_cs_n(spi_cs_n[0]),
        .last_rx_data(slave0_rx_data),
        .rx_done(slave0_rx_done),
        .transaction_count(slave0_tx_count)
    );
    
    // SPI Slave 1 instantiation
    spi_slave #(
        .DATA_WIDTH(DATA_WIDTH),
        .SLAVE_ID(8'hB1)  // Slave 1 ID
    ) slave1_inst (
        .clk(clk),
        .rst_n(rst_n),
        .spi_sclk(spi_sclk),
        .spi_mosi(spi_mosi),
        .spi_miso(spi_miso_slave1),
        .spi_cs_n(spi_cs_n[1]),
        .last_rx_data(slave1_rx_data),
        .rx_done(slave1_rx_done),
        .transaction_count(slave1_tx_count)
    );

endmodule
