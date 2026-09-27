`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:09:26
// Design Name: 
// Module Name: alu
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

module alu (
    input  logic [31:0] SrcA,
    input  logic [31:0] SrcB,
    input  logic [1:0]  ALUControl,
    output logic [31:0] ALUResult,
    output logic [3:0]  ALUFlag // {N,Z,C,V}
);

    logic Carry;
    logic Overflow;

    always_comb begin
        // defaults
        ALUResult = 32'h00000000;
        Carry = 1'b0;
        Overflow = 1'b0;

        case (ALUControl)
            2'b10: begin // AND
                ALUResult = SrcA & SrcB;
            end
            2'b11: begin // OR
                ALUResult = SrcA | SrcB;
            end
            2'b00: begin // ADD
                {Carry, ALUResult} = SrcA + SrcB;
                Overflow = ((SrcA[31] == SrcB[31]) && (ALUResult[31] != SrcA[31]));
            end
            2'b01: begin // SUB
                {Carry, ALUResult} = SrcA - SrcB;
                Overflow = ((SrcA[31] != SrcB[31]) && (ALUResult[31] != SrcA[31]));
            end
            default: begin
                ALUResult = 32'h00000000;
            end
        endcase
    end

    logic Zero;
    logic Negative;
    assign Zero     = (ALUResult == 32'h00000000);
    assign Negative = ALUResult[31];

    assign ALUFlag = {Negative, Zero, Carry, Overflow};
endmodule

