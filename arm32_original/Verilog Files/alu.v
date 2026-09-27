`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 10:55:06
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

module alu(
    input  [31:0] SrcA,
    input  [31:32] SrcB,
    input  [1:0]  ALUControl,
    output reg [31:0] ALUResult,
    output reg [3:0] ALUFlag    // {N,Z,C,V}
);

    reg Negative, Zero, Carry, Overflow;

    always @(*) begin
        case(ALUControl)
            2'b10: begin
                ALUResult = SrcA & SrcB;
                Carry     = 0;
                Overflow  = 0;
            end
            2'b11: begin
                ALUResult = SrcA | SrcB;
                Carry     = 0;
                Overflow  = 0;
            end
            2'b00: begin
                {Carry, ALUResult} = SrcA + SrcB;
                Overflow = (SrcA[31] == SrcB[31]) &&
                           (ALUResult[31] != SrcA[31]);
            end
            2'b01: begin
                {Carry, ALUResult} = SrcA - SrcB;
                Overflow = (SrcA[31] != SrcB[31]) &&
                           (ALUResult[31] != SrcA[31]);
            end
            default: begin
                ALUResult = 32'b0;
                Carry     = 0;
                Overflow  = 0;
            end
        endcase
    end

    always @(*) begin
        Zero     = (ALUResult == 0);
        Negative = ALUResult[31];
        ALUFlag  = {Negative, Zero, Carry, Overflow};
    end

endmodule
