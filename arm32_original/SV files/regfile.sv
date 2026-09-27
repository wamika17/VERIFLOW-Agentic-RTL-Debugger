`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:17:47
// Design Name: 
// Module Name: regfile
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


module regfile (
    input  logic        clk,
    input  logic        we3,
    input  logic [3:0]  ra1, ra2, wa3,
    input  logic [31:0] wd3, r15,
    output logic [31:0] rd1, rd2
);
    logic [31:0] rf [0:14];

    assign rd1 = (ra1 == 4'hF) ? r15 : rf[ra1];
    assign rd2 = (ra2 == 4'hF) ? r15 : rf[ra2];

    always_ff @(posedge clk) begin
        if (we3 && (wa3 != 4'hF)) rf[wa3] <= wd3; // don't write PC register slot
    end
endmodule

