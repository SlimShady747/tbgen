// Generatated test bench (sample tbgen.py template with lower level macros)
`default_nettype none
%%%TIMESCALE%%%
  module tb_top;
%%%WIRES%%%
%%%UUTMOD%%% uut (
%%%ARGS%%% );
parameter PERIOD=%%%NPERIOD%%%;
always 
  #(PERIOD/2) %%%CSIGNAL%%%=~%%%CSIGNAL%%%;

initial begin
  $dumpfile("%%%UUTMOD%%%.vcd");
  $dumpvars(%%%DLEVEL%%%,tb_top);
   %%%RSIGNAL%%%=%%%RPOLARITY%%%;
   #(PERIOD*2) %%%RSIGNAL%%%=~%%%RSIGNAL%%%;
   #PERIOD %%%RSIGNAL%%%=~%%%RSIGNAL%%%;
end
   
// Include your custom changes in the included file
`include "%%%INCLUDEFILE%%%"

endmodule
