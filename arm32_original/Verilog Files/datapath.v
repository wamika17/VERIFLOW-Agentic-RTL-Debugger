`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 10:59:53
// Design Name: 
// Module Name: datapath
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

`include "extend.v"
`include "alu.v"
`include "regfile.v"
`include "mux2.v"
`include "flopr.v"
`include "adder.v"

module datapath(
    input        clk,
    input        reset,
    input  [1:0] RegSrc,
    input        RegWrite,
    input  [1:0] ImmSrc,
    input        ALUSrc,
    input  [1:0] ALUControl,
    input        MemtoReg,
    input        PCSrc,
    output reg [3:0]  ALUFlags,
    output reg [31:0] PC,
    input  [31:0] Instr,
    output reg [31:0] ALUResult,
    output reg [31:0] WriteData,
    input  [31:0] ReadData
);

    wire [31:0] PCNext, PCPlus4, PCPlus8;
    wire [31:0] ExtImm, SrcA, SrcB, Result;
    wire [3:0] RA1, RA2;

    mux2 #(.WIDTH(32)) pcmux(PCPlus4, Result, PCSrc, PCNext);
    flopr pcreg(clk, reset, PCNext, PC);

    adder pcadd1(PC,      32'd4, PCPlus4);
    adder pcadd2(PCPlus4, 32'd4, PCPlus8);

    mux2 #(.WIDTH(4)) ra1mux(Instr[19:16], 4'b1111,     RegSrc[0], RA1);
    mux2 #(.WIDTH(4)) ra2mux(Instr[3:0],   Instr[15:12], RegSrc[1], RA2);

    regfile rf(clk, RegWrite, RA1, RA2,
               Instr[15:12], Result, PCPlus8, SrcA, WriteData);

    mux2 #(.WIDTH(32)) resmux(ALUResult, ReadData, MemtoReg, Result);
    extend ext(Instr[23:0], ImmSrc, ExtImm);

    mux2 #(.WIDTH(32)) srcbmux(WriteData, ExtImm, ALUSrc, SrcB);
    alu alu_unit(SrcA, SrcB, ALUControl, ALUResult, ALUFlags);

endmodule

