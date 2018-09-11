`default_nettype none
module top(input clk, input rst, input run, input hold, output LED1, output LED2, output LED3,
	   output LED4, output LED5);

   
   reg [2:0] 	  count=0;  // I reduced this down from 15:0 so the simulation would be manageable
   reg [7:0] 	  ctimer=0;
 	  
   reg 		  go=0;
   
		
// I also reduced 250 to 25 to speed up simulation
   
/*
 Simple state machine
 
  CW - n=n+1,  led-on ctimer=250, >CWAIT 
  CWAIT - wait for timer, if n==3 >CCW else >CW
  CCW - n=n-1, led-on ctimer=250, CCWAIT
  CCWAIT - wait for timer, if n==0 >CW else CCW

 */

// dense encoding
   localparam CW = 2'b00;
   localparam CWAIT = 2'b01;
   localparam CCW = 2'b10;
   localparam CCWAIT = 2'b11;
   

   reg [1:0] state=CW;
   reg [3:0] leds=1;
   reg 	     blink=0;
   



   assign LED1=leds[0];
   assign LED2=leds[1];
   assign LED3=leds[2];
   assign LED4=leds[3];
   assign LED5=blink;
   

    


   always @(posedge clk)
     begin
// Handle reset
	if (rst) 
	  begin
	     count<=0;
	     ctimer<=0;
	  end
// Handle run/hold inputs
	if (~go & run) begin
	   go<=1'b1;
	end
	if (go & hold ) begin
	  go<=1'b0;
	  count<=3;  // anything to keep it off zero
	end
	   
// This works because the CW and CCW states are only active one time before CWAIT or CCWAIT
// So if you freeze the count, you freeze the state machine in CWAIT or CCWAIT within one cycle
	if (go) count<=count+1;  // freeze the count on hold

	
// The rest of the state machine is pretty easy
// count down the timer to 0 when count==0
// The CWAIT and CCWAIT states will do nothing until the timer expires
// we also freeze ctimer even though that should not be necessary
	if (go && ctimer!=0 && count==0) ctimer<=ctimer-1;
	case (state)
	     CW:
	       begin
		  leds={leds[2:0],1'b0};
		  ctimer<=25;
		  blink<=~blink;
		  state<=CWAIT;
	       end
   	     CWAIT:
	       begin
		  if (ctimer==0)
		    begin
		       state<=leds[3]?CCW:CW;
		    end
	       end
	  CCW:
	    begin
	       leds={1'b0,leds[3:1]};
	       blink<=~blink;
	       ctimer<=25;
	       state=CCWAIT;
	    end
	  CCWAIT:
	    begin
	       if (ctimer==0)
		 begin
		    state<=leds[0]?CW:CCW;
		 end
	    end
	  default:
	    begin
	       state<=CW;  // never gets here we hope
	    end
	endcase // case (state)
     end
   

endmodule // top
