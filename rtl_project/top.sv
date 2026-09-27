module top (
    input  logic a,
    input  logic b,
    output logic y
);

    logic alu_out;

    alu u_alu (
        .a(a),
        .b(b),
        .result(alu_out)
    );

    assign y = missing signal;

endmodule
