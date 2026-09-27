`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:14:00
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

module extend (
    input  logic [23:0] Instr,
    input  logic [1:0]  ImmSrc,
    output logic [31:0] ExtImm
);
    always_comb begin
        case (ImmSrc)
            2'b00: ExtImm = {24'b0, Instr[7:0]};                     // 8-bit zero ext
            2'b01: ExtImm = {20'b0, Instr[11:0]};                    // 12-bit zero ext
            2'b10: ExtImm = {{6{Instr[23]}}, Instr[23:0], 2'b00};     // branch/shifted signed ext
            default: ExtImm = 32'hXXXXXXXX;
        endcase
    end
endmodule

