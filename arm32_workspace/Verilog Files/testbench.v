`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 11:08:45
// Design Name: 
// Module Name: testbench
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

`include "top.v"

module testbench;

    reg clk;
    reg reset;

    top dut(clk, reset);

    initial begin
        clk = 0;
        reset = 1;
        #10 reset = 0;
    end

    always #5 clk = ~clk;

    initial begin
        #10000;
        if (dut.cpu_core.dp.rf.rf[5] === 32'd11)
            $display("TEST PASSED: R5 = 11");
        else
            $display("TEST FAILED: R5 = %d", dut.cpu_core.dp.rf.rf[5]);

        $finish;
    end

endmodule
