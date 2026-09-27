`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 11:03:53
// Design Name: 
// Module Name: flopr
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

module flopr(
    input        clk,
    input        reset,
    input  [31:0] d,
    output reg [31:0] q
);

    always @(posedge clk or posedge reset)
        if (reset)
            q <= 32'b0;
        else
            q <= d;

endmodule

