`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 10:56:56
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


`include "condcheck.v"
`include "flopenr.v"

module condlogic(
    input        clk,
    input        reset,
    input  [3:0] Cond,
    input  [3:0] ALUFlags,
    input  [1:0] FlagW,
    input        PCS,
    input        RegW,
    input        MemW,
    output reg   PCSrc,
    output reg   RegWrite,
    output reg   MemWrite
);

    wire [1:0] FlagWrite;
    wire [3:0] Flags;
    wire CondEx;

    flopenr #(.WIDTH(2)) flagreg1(clk, reset, FlagWrite[1],
                                  ALUFlags[3:2], Flags[3:2]);

    flopenr #(.WIDTH(2)) flagreg0(clk, reset, FlagWrite[0],
                                  ALUFlags[1:0], Flags[1:0]);

    condcheck ck(Cond, Flags, CondEx);

    assign FlagWrite = FlagW & {2{CondEx}};

    always @(*) begin
        RegWrite = RegW & CondEx;
        MemWrite = MemW & CondEx;
        PCSrc    = PCS  & CondEx;
    end

endmodule
