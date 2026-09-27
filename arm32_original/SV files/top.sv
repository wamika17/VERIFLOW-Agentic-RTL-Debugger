`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:19:51
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

`include "cpu.sv"
`include "imem.sv"
`include "dmem.sv"

module top (
    input  logic clk,
    input  logic reset
);
    logic [31:0] PC;
    logic [31:0] Instr;
    logic        MemWrite;
    logic [31:0] ALUResult, WriteData, ReadData;
    logic [31:0] DataAdr;

    cpu cpu0(.clk(clk), .reset(reset),
             .PC(PC), .Instr(Instr),
             .MemWrite(MemWrite),
             .ALUResult(ALUResult), .WriteData(WriteData),
             .ReadData(ReadData));

    imem im(.a(PC), .rd(Instr));
    dmem dm(.clk(clk), .we(MemWrite), .a(ALUResult), .wd(WriteData), .rd(ReadData));
endmodule
