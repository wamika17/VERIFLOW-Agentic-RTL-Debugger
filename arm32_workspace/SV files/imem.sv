`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:18:20
// Design Name: 
// Module Name: imem
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module imem (
    input  logic [31:0] a,
    output logic [31:0] rd
);
    logic [31:0] RAM [0:63];

    initial begin
        // memfile.dat must be in working dir or project sources_1/new
     $readmemh("D:/Vivado_Projects/ARm_32_BIT_CPU_DESIGN_VERILOG/ARm_32_BIT_CPU_DESIGN_VERILOG.srcs/sim_1/imports/new/memfile.dat", RAM);
    end
    assign rd = RAM[a[31:2]]; // word aligned
endmodule

