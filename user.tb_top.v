initial 
begin
   run=1'b0;
   hold=1'b0;
   #(PERIOD*10) run=1'b1;
   #PERIOD run=1'b0;
   #(PERIOD*1024) hold=1'b1;
   #PERIOD hold=1'b0;
   #(PERIOD*100)
   $finish;
end   
