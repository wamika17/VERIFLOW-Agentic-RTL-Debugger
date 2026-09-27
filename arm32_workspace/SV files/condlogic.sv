`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:10:57
// Design Name: 
// Module Name: condlogic
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

`include "flopenr.sv"
`include "condcheck.sv"

module condlogic (
    input  logic        clk,
    input  logic        reset,
    input  logic [3:0]  Cond,
    input  logic [3:0]  ALUFlags,
    input  logic [1:0]  FlagW,
    input  logic        PCS,
    input  logic        RegW,
    input  logic        MemW,
    output logic        PCSrc,
    output logic        RegWrite,
    output logic        MemWrite
);
    logic [1:0] FlagWrite;
    logic [3:0] Flags;
    logic CondEx;

    // two flag registers (top bit pair and bottom bit pair)
    flopenr #(.WIDTH(2)) flagreg1(.clk(clk), .reset(reset), .en(FlagWrite[1]),
                                  .d(ALUFlags[3:2]), .q(Flags[3:2]));
    flopenr #(.WIDTH(2)) flagreg0(.clk(clk), .reset(reset), .en(FlagWrite[0]),
                                  .d(ALUFlags[1:0]), .q(Flags[1:0]));

    condcheck cc(.Cond(Cond), .Flags(Flags), .CondEx(CondEx));

    assign FlagWrite = FlagW & {2{CondEx}};
    assign RegWrite  = RegW & CondEx;
    assign MemWrite  = MemW & CondEx;
    assign PCSrc     = PCS & CondEx;
endmodule

