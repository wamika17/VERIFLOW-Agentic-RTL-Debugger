`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 11:04:26
// Design Name: 
// Module Name: flopenr
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

module flopenr #(parameter WIDTH = 8)(
    input              clk,
    input              reset,
    input              en,
    input  [WIDTH-1:0] d,
    output reg [WIDTH-1:0] q
);

    always @(posedge clk or posedge reset)
        if (reset)
            q <= {WIDTH{1'b0}};
        else if (en)
            q <= d;

endmodule

