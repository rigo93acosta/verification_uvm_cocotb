module fifo #(
    parameter WIDTH = 8,
    parameter DEPTH = 8
)(
    input  wire              clk,
    input  wire              rst_n,

    input  wire              push,
    input  wire              pop,
    input  wire [WIDTH-1:0]  data_in,

    output reg  [WIDTH-1:0]  data_out,
    output wire              full,
    output wire              empty
);

    // -------------------------------------------------
    // Parámetros derivados
    // -------------------------------------------------
    localparam ADDR_WIDTH = $clog2(DEPTH);

    // -------------------------------------------------
    // Memoria
    // -------------------------------------------------
    reg [WIDTH-1:0] mem [0:DEPTH-1];

    // -------------------------------------------------
    // Punteros y contador
    // -------------------------------------------------
    reg [ADDR_WIDTH-1:0] wr_ptr;
    reg [ADDR_WIDTH-1:0] rd_ptr;
    reg [ADDR_WIDTH:0]   count;  // hasta DEPTH

    // -------------------------------------------------
    // Flags
    // -------------------------------------------------
    assign full  = (count == DEPTH);
    assign empty = (count == 0);

    // -------------------------------------------------
    // Lógica principal
    // -------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr   <= 0;
            rd_ptr   <= 0;
            count    <= 0;
            data_out <= 0;
        end else begin

            // -----------------------------
            // PUSH
            // -----------------------------
            if (push && !full) begin
                mem[wr_ptr] <= data_in;
                wr_ptr <= wr_ptr + 1;
            end

            // -----------------------------
            // POP
            // -----------------------------
            if (pop && !empty) begin
                data_out <= mem[rd_ptr];
                rd_ptr <= rd_ptr + 1;
            end

            // -----------------------------
            // COUNT update
            // -----------------------------
            case ({push && !full, pop && !empty})
                2'b10: count <= count + 1; // solo push
                2'b01: count <= count - 1; // solo pop
                2'b11: count <= count;     // push y pop simultáneo
                default: count <= count;
            endcase

        end
    end

endmodule