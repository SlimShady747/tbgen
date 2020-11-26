`include "./full_adder.v"
`timescale 1ns/10ps //Adjust to suit

module tb_full_adder;

reg         a        ;
reg         b        ;
reg         c_in     ;
wire        s        ;
wire        c_out    ;

full_adder uut (
    .a        (    a        ),
    .b        (    b        ),
    .c_in     (    c_in     ),
    .s        (    s        ),
    .c_out    (    c_out    )
);

parameter PERIOD = 10; //adjust for your timescale

initial begin
    $dumpfile("tb_output.vcd");
    $dumpvars(2, tb_full_adder);
    clk = 1'b0;
    #(PERIOD/2);
    forever
        #(PERIOD/2) clk = ~clk;
end

initial begin
        rst=1'b0;
         #(PERIOD*2) rst=~rst;
         #PERIOD rst=~rst;
         end
endmodule
