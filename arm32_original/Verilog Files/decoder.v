`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.11.2025 11:01:03
// Design Name: 
// Module Name: decoder
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
module decoder(
    input  [1:0] Op,
    input  [5:0] Funct,
    input  [3:0] Rd,
    output [1:0] FlagW,     // note: outputs driven from procedural block below
    output PCS,
    output RegW,
    output MemW,
    output MemtoReg,
    output ALUSrc,
    output [1:0] ImmSrc,
    output [1:0] RegSrc,
    output [1:0] ALUControl
);

    // internal control vector (set procedurally)
    reg [9:0] controls; // {Branch, MemtoReg, MemW, ALUSrc, ImmSrc[1:0], RegW, RegSrc[1:0], ALUOp}
    reg [1:0] flagw_r;
    reg [1:0] alu_ctrl_r;

    // unpacked outputs as wires driven by 'controls' (these must be wires)
    wire Branch;
    wire MemtoReg_w;
    wire MemW_w;
    wire ALUSrc_w;
    wire [1:0] ImmSrc_w;
    wire RegW_w;
    wire [1:0] RegSrc_w;
    wire ALUOp_w;

    // continuous assignment: unpack controls into wires
    assign {Branch, MemtoReg_w, MemW_w, ALUSrc_w, ImmSrc_w, RegW_w, RegSrc_w, ALUOp_w} = controls;

    // Connect wires to module outputs
    assign MemtoReg = MemtoReg_w;
    assign MemW      = MemW_w;
    assign ALUSrc    = ALUSrc_w;
    assign ImmSrc    = ImmSrc_w;
    assign RegW      = RegW_w;
    assign RegSrc    = RegSrc_w;

    // PCS is computed procedurally below; make it a wire and drive from reg RegW_r/Branch
    wire PCS_w;
    assign PCS = PCS_w;

    // main decoder: set 'controls' based on Op / Funct
    always @(*) begin
        case (Op)
            2'b00: begin
                if (Funct[5])
                    controls = 10'b0001001001; // data-processing immediate (example pattern)
                else
                    controls = 10'b0000001001; // data-processing register
            end
            2'b01: begin
                if (Funct[0])
                    controls = 10'b0101011000; // LDR
                else
                    controls = 10'b0011010100; // STR
            end
            2'b10: controls = 10'b1001100010; // Branch
            default: controls = 10'b0000000000;
        endcase
    end

    // ALU decoder & FlagW logic (procedural to drive reg outputs)
    always @(*) begin
        // default values
        alu_ctrl_r = 2'b00;
        flagw_r   = 2'b00;

        if (ALUOp_w) begin
            case (Funct[4:1])
                4'b0100: alu_ctrl_r = 2'b00; // ADD
                4'b0010: alu_ctrl_r = 2'b01; // SUB
                4'b0000: alu_ctrl_r = 2'b10; // AND
                4'b1100: alu_ctrl_r = 2'b11; // ORR
                default: alu_ctrl_r = 2'b00;
            endcase
            flagw_r[1] = Funct[0];
            flagw_r[0] = Funct[0] & ( (alu_ctrl_r == 2'b00) || (alu_ctrl_r == 2'b01) );
        end
    end

    // PCS logic: procedural assignment to a reg and drive PCS_w
    reg pcs_reg;
    always @(*) begin
        pcs_reg = ( (Rd == 4'b1111) && RegW_w ) || Branch;
    end
    assign PCS_w = pcs_reg;

    // drive the module outputs that need to be regs via continuous assignment from reg vars
    // FlagW and ALUControl are declared as outputs, but they were reg-like in original;
    // to keep simple, we output them using continuous assignment from reg values:
    assign FlagW = flagw_r;
    assign ALUControl = alu_ctrl_r;

endmodule
