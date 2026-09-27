`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:12:53
// Design Name: 
// Module Name: decoder
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


module decoder (
    input  logic [1:0] Op,
    input  logic [5:0] Funct,
    input  logic [3:0] Rd,
    output logic [1:0] FlagW,
    output logic PCS,
    output logic RegW,
    output logic MemW,
    output logic MemtoReg,
    output logic ALUSrc,
    output logic [1:0] ImmSrc,
    output logic [1:0] RegSrc,
    output logic [1:0] ALUControl
);
    // controls bits: {Branch, MemtoReg, MemW, ALUSrc, ImmSrc[1:0], RegW, RegSrc[1:0], ALUOp}
    logic [9:0] controls;
    logic Branch;
    logic ALUOp;

    always_comb begin
        // default
        controls = 10'bx;
        unique case (Op)
            2'b00: begin
                if (Funct[5]) controls = 10'b0_0_0_1_00_1_00_1; // Data-processing immediate (example)
                else          controls = 10'b0_0_0_0_00_1_00_1; // Data-processing register
            end
            2'b01: begin
                if (Funct[0]) controls = 10'b0_1_0_1_00_0_00_0; // LDR (example)
                else          controls = 10'b0_0_1_1_00_0_01_0; // STR
            end
            2'b10: begin
                controls = 10'b1_0_0_0_00_0_00_0; // B (branch)
            end
            default: controls = 10'bx;
        endcase
    end

    // break controls into named outputs
    assign {Branch, MemtoReg, MemW, ALUSrc, ImmSrc, RegW, RegSrc, ALUOp} = controls;

    // ALU decode & flag write
    always_comb begin
        if (ALUOp) begin
            unique case (Funct[4:1])
                4'b0100: ALUControl = 2'b00; // ADD
                4'b0010: ALUControl = 2'b01; // SUB
                4'b0000: ALUControl = 2'b10; // AND
                4'b1100: ALUControl = 2'b11; // ORR
                default: ALUControl = 2'bxx;
            endcase
            FlagW[1] = Funct[0];
            FlagW[0] = Funct[0] && (ALUControl == 2'b00 || ALUControl == 2'b01);
        end else begin
            ALUControl = 2'b00;
            FlagW = 2'b00;
        end
    end

    assign PCS = ((Rd == 4'b1111) && RegW) || Branch;
endmodule

