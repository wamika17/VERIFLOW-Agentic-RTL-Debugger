`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:09:59
// Design Name: 
// Module Name: alutest
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

`timescale 1ns/1ps
module alutest;
    logic [31:0] SrcA, SrcB;
    logic [1:0]  ALUControl;
    logic [31:0] ALUResult;
    logic [3:0]  ALUFlag;

    alu uut(.SrcA(SrcA), .SrcB(SrcB), .ALUControl(ALUControl),
            .ALUResult(ALUResult), .ALUFlag(ALUFlag));

    initial begin
        $display("ALU self test start");
        SrcA = 32'h4; SrcB = 32'h5;
        #10 ALUControl = 2'b00; // ADD
        #10 ALUControl = 2'b01; // SUB
        #10 ALUControl = 2'b10; // AND
        #10 ALUControl = 2'b11; // OR
        #10 $finish;
    end

    initial begin
        $dumpfile("alutest.vcd");
        $dumpvars(0, alutest);
    end
endmodule

