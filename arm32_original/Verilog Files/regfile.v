`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 11:07:28
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


module regfile(
    input        clk,
    input        we3,
    input  [3:0] ra1,
    input  [3:0] ra2,
    input  [3:0] wa3,
    input  [31:0] wd3,
    input  [31:0] r15,
    output [31:0] rd1,
    output [31:0] rd2
);

    reg [31:0] rf[0:14];    // R0–R14

    assign rd1 = (ra1 == 4'b1111) ? r15 : rf[ra1];
    assign rd2 = (ra2 == 4'b1111) ? r15 : rf[ra2];

    always @(posedge clk)
        if (we3)
            rf[wa3] <= wd3;

endmodule

