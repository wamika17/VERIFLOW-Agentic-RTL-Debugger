`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 11:04:54
// Design Name: 
// Module Name: imem
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
//////////////////////////////////////////////////////////////////////////////
module imem(input [31:0] a, output [31:0] rd);
  reg [31:0] RAM [0:63];

  initial begin
      $readmemh("memfile.dat", RAM);
  end

  assign rd = RAM[a[31:2]];
endmodule
