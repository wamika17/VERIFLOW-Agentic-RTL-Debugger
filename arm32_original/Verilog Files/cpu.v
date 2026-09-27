`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 10:58:58
// Design Name: 
// Module Name: cpu
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

`include "controller.v"
`include "datapath.v"

module cpu(
    input        clk,
    input        reset,
    output [31:0] PC,
    input  [31:0] Instr,
    output        MemWrite,
    output [31:0] ALUResult,
    output [31:0] WriteData,
    input  [31:0] ReadData
);

    wire [3:0] ALUFlags;
    wire RegWrite, ALUSrc, MemtoReg, PCSrc;
    wire [1:0] RegSrc, ImmSrc, ALUControl;

    controller c(
        clk, reset,
        Instr[31:12], ALUFlags,
        RegSrc, RegWrite, ImmSrc,
        ALUSrc, ALUControl,
        MemWrite, MemtoReg, PCSrc
    );

    datapath dp(
        clk, reset,
        RegSrc, RegWrite, ImmSrc,
        ALUSrc, ALUControl,
        MemtoReg, PCSrc,
        ALUFlags, PC, Instr,
        ALUResult, WriteData, ReadData
    );

endmodule
