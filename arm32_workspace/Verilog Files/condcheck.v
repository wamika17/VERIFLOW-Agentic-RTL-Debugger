`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 10:56:26
// Design Name: 
// Module Name: condcheck
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

module condcheck(
    input  [3:0] Cond,
    input  [3:0] Flags,
    output reg   CondEx
);

    wire neg, zero, carry, overflow;
    wire ge;

    assign {neg, zero, carry, overflow} = Flags;
    assign ge = ~(neg ^ overflow);

    always @(*) begin
        case (Cond)
            4'b0000: CondEx = zero;              // EQ
            4'b0001: CondEx = ~zero;             // NE
            4'b0010: CondEx = carry;             // CS
            4'b0011: CondEx = ~carry;            // CC
            4'b0100: CondEx = neg;               // MI
            4'b0101: CondEx = ~neg;              // PL
            4'b0110: CondEx = overflow;          // VS
            4'b0111: CondEx = ~overflow;         // VC
            4'b1000: CondEx = carry & ~zero;     // HI
            4'b1001: CondEx = ~(carry & ~zero);  // LS
            4'b1010: CondEx = ge;                // GE
            4'b1011: CondEx = ~ge;               // LT
            4'b1100: CondEx = ~zero & ge;        // GT
            4'b1101: CondEx = ~(~zero & ge);     // LE
            4'b1110: CondEx = 1'b1;              // AL
            default: CondEx = 1'b0;
        endcase
    end

endmodule

