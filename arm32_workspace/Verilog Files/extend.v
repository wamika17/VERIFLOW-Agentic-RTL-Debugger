`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 11:03:13
// Design Name: 
// Module Name: extend
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

module extend(
    input  [23:0] Instr,
    input  [1:0]  ImmSrc,
    output reg [31:0] ExtImm
);

    always @(*) begin
        case (ImmSrc)
            2'b00: ExtImm = {24'b0, Instr[7:0]};                 // zero-extend 8-bit
            2'b01: ExtImm = {20'b0, Instr[11:0]};                // zero-extend 12-bit
            2'b10: ExtImm = {{6{Instr[23]}}, Instr[23:0], 2'b00}; // sign-extend + shift
            default: ExtImm = 32'b0;
        endcase
    end

endmodule
