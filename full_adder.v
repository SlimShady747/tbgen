// full adder.v

module full_adder (input a,
                   input b,       
                   input c_in,    
                   output s,      
                   output c_out);
    
    assign {c_out,s} = a + b + c_in;
    
endmodule //End Of Module full_adder
