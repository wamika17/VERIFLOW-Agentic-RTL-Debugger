`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:16:16
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


`include "mux2.sv"
`include "flopr.sv"
`include "flopenr.sv"
`include "adder.sv"
`include "regfile.sv"
`include "extend.sv"
`include "alu.sv"

module datapath (
    input  logic clk,
    input  logic reset,
    input  logic [1:0] RegSrc,
    input  logic RegWrite,
    input  logic [1:0] ImmSrc,
    input  logic ALUSrc,
    input  logic [1:0] ALUControl,
    input  logic MemtoReg,
    input  logic PCSrc,
    output logic [3:0] ALUFlags,
    output logic [31:0] PC,
    input  logic [31:0] Instr,
    output logic [31:0] ALUResult,
    output logic [31:0] WriteData,
    input  logic [31:0] ReadData
);
    logic [31:0] PCNext, PCPlus4, PCPlus8;
    logic [31:0] ExtImm, SrcA, SrcB, Result;
    logic [3:0] RA1, RA2;

    // PC logic
    mux2 #(.WIDTH(32)) pcmux(.d0(PCPlus4), .d1(Result), .s(PCSrc), .y(PCNext));
    flopr pcreg(.clk(clk), .reset(reset), .d(PCNext), .q(PC));
    adder pcadd1(.a(PC), .b(32'h4), .y(PCPlus4));
    adder pcadd2(.a(PCPlus4), .b(32'h4), .y(PCPlus8));

    // register addressing and register file
    mux2 #(.WIDTH(4)) ra1mux(.d0(Instr[19:16]), .d1(4'hF), .s(RegSrc[0]), .y(RA1));
    mux2 #(.WIDTH(4)) ra2mux(.d0(Instr[3:0]), .d1(Instr[15:12]), .s(RegSrc[1]), .y(RA2));

    regfile rf(.clk(clk), .we3(RegWrite), .ra1(RA1), .ra2(RA2),
               .wa3(Instr[15:12]), .wd3(Result), .r15(PCPlus8),
               .rd1(SrcA), .rd2(WriteData));

    mux2 #(.WIDTH(32)) resmux(.d0(ALUResult), .d1(ReadData), .s(MemtoReg), .y(Result));
    extend ext(.Instr(Instr[23:0]), .ImmSrc(ImmSrc), .ExtImm(ExtImm));

    // ALU input mux
    mux2 #(.WIDTH(32)) srcbmux(.d0(WriteData), .d1(ExtImm), .s(ALUSrc), .y(SrcB));
    alu alu_unit(.SrcA(SrcA), .SrcB(SrcB), .ALUControl(ALUControl),
                 .ALUResult(ALUResult), .ALUFlag(ALUFlags));
endmodule
