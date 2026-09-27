`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 11:01:44
// Design Name: 
// Module Name: dmem
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

module dmem(
    input        clk,
    input        we,
    input  [31:0] a,
    input  [31:0] wd,
    output reg [31:0] rd
);

    reg [31:0] RAM[0:63];

    always @(posedge clk)
        if (we)
            RAM[a[31:2]] <= wd;

    always @(*)
        rd = RAM[a[31:2]];

endmodule

