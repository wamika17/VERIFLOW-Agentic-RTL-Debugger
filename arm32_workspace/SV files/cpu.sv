`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:20:28
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


`include "controller.sv"
`include "datapath.sv"

module cpu (
    input  logic clk,
    input  logic reset,
    output logic [31:0] PC,
    input  logic [31:0] Instr,
    output logic MemWrite,
    output logic [31:0] ALUResult,
    output logic [31:0] WriteData,
    input  logic [31:0] ReadData
);
    logic [3:0] ALUFlags;
    logic RegWrite, ALUSrc, MemtoReg, PCSrc;
    logic [1:0] RegSrc, ImmSrc, ALUControl;

    controller c(.clk(clk), .reset(reset), .Instr(Instr[31:12]), .ALUFlags(ALUFlags),
                 .RegSrc(RegSrc), .RegWrite(RegWrite), .ImmSrc(ImmSrc),
                 .ALUSrc(ALUSrc), .ALUControl(ALUControl),
                 .MemWrite(MemWrite), .MemtoReg(MemtoReg), .PCSrc(PCSrc));

    datapath dp(.clk(clk), .reset(reset), .RegSrc(RegSrc), .RegWrite(RegWrite),
                .ImmSrc(ImmSrc), .ALUSrc(ALUSrc), .ALUControl(ALUControl),
                .MemtoReg(MemtoReg), .PCSrc(PCSrc),
                .ALUFlags(ALUFlags), .PC(PC), .Instr(Instr),
                .ALUResult(ALUResult), .WriteData(WriteData), .ReadData(ReadData));
endmodule
