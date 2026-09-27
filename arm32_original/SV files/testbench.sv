`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 12:19:05
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

`timescale 1ns/1ps
`include "top.sv"

module testbench;

    logic clk;
    logic reset;

    // Instantiate DUT
    top dut (
        .clk(clk),
        .reset(reset)
    );

    // Clock generation (10ns period → 100MHz)
    always #5 clk = ~clk;

    // Reset sequence
    initial begin
        clk = 0;
        reset = 1;
        #20 reset = 0;
    end

    // Waveform dump
    initial begin
        $dumpfile("cpu_sim.vcd");
        $dumpvars(0, testbench);   // dump entire DUT hierarchy
    end

    // End simulation
    initial begin
        #20000;   // run for 20 us
        $finish;
    end

endmodule

