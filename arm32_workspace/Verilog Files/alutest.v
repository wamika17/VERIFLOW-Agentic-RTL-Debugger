`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 10:55:46
// Design Name: 
// Module Name: alutest
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

`include "alu.v"

module alutest;

    reg [31:0] SrcA, SrcB;
    reg [1:0]  ALUControl;
    wire [31:0] ALUResult;
    wire [3:0]  ALUFlag;

    alu dut(.SrcA(SrcA), .SrcB(SrcB),
            .ALUControl(ALUControl),
            .ALUResult(ALUResult),
            .ALUFlag(ALUFlag));

    initial begin
        SrcA = 32'h4; 
        SrcB = 32'h5;

        #10 ALUControl = 2'b00;  // add
        #10 ALUControl = 2'b01;  // sub
        #10 ALUControl = 2'b10;  // and
        #10 ALUControl = 2'b11;  // or

        #50 $finish;
    end

endmodule