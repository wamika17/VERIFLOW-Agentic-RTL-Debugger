`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 11:08:08
// Design Name: 
// Module Name: top
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

`include "cpu.v"
`include "imem.v"
`include "dmem.v"

module top(
    input clk,
    input reset
);

    wire [31:0] PC, Instr, ReadData;
    wire [31:0] WriteData, DataAdr;
    wire        MemWrite;

    cpu cpu_core(
        clk, reset,
        PC, Instr, MemWrite,
        DataAdr, WriteData, ReadData
    );

    imem imem_i(
        PC, Instr
    );

    dmem dmem_i(
        clk, MemWrite,
        DataAdr, WriteData, ReadData
    );

endmodule
