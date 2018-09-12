Testbench generator
===================

Give me your verilog code, I will give you a testbench for it.

How to use?
-----------

Make sure you have python on your system.

    python tbgen.py input_verilog_file_name [output_testbench_file_name]

----

Author: Xiongfei(Alex) Guo <xfguo@credosemi.com>

License: Beerware

Updates by Al Williams (Hackaday)
=================================

I made a few changes:
1. Put a placeholder timescale up front. If you want to change back to the old behavior you
can rename print_module_head_orig to print_module_head (and delete the current one) or at the
bottom change print_module_head to print_module_head_orig.
2. Generate a reset if reset is detected.
3. Put comments in the generated file.
4. Put an include for your user-generated code. This is important because if you change the generated file and regenerate it, you'll lose your changes.
5. Changed $dumpvars to level 2
6. Added a simple example
7. Added command line options
8. Based testbench on optional template file

Nothing major, and -- of course -- this is just a template to get you started but don't forget
that any changes you make will be clobbered if you regenerate the testbench!

Example
-------

    python tbgen.py top.v top.tb.v
    iverilog top.tb.v top.v -o top
    vvp top
    gtkwave tb_output.vcd

Or try http://edaplayground.com if you don't want to install iverilog and gtkwave.

Command line
------------
    usage: tbgen.py [-h] [-p PERIOD] [-t TIMESCALE] [-d DUMPFILE] [-l LEVEL] [-r]
                    input_file [output_file]
    
    Automatically generate Verilog testbench
    
    positional arguments:
      input_file            input Verilog file
      output_file           output Verilog testbench
    
    optional arguments:
      -h, --help            show this help message and exit
      -p PERIOD, --period PERIOD
                            set period in clock ticks (default=10)
      -t TIMESCALE, --timescale TIMESCALE
                            set timescale (default=1ns/10ps)
      -d DUMPFILE, --dumpfile DUMPFILE
                            set dumpfile (default=tb_output.vcd)
      -l LEVEL, --level LEVEL
                            set dump depth level (usually 0,1, or 2; default=2)
      -r, --resetneg        set reset to negative (default positive)			    
      -i INCLUDE, --include INCLUDE
                            sets user include file name (default=user.tb_<name>.v)
      -T TEMPLATE, --template TEMPLATE
                            sets template (default=use internal template; -T ?
                            will dump internal template and exit -- requires dummy
                            input name)

Templates
---------
There is a default template for creating the testbench inside the program. You can also
use your own. To dump the default template, use a phony input name and pass -T ? to the
program. It will write the template to the output file (or the terminal if you don't give
it an output file).

The template file can have anything you want in it and placeholders will get rewritten.
You can omit placeholders (for example, if you don't want the reset code, leave out
the reset placeholder.

Here are the known placeholders:
```    
    %%%TIMESCALE%%%% - The entire timescale directive (If you prefer to use an include here, just omit this and put the include in your template)
    %%%HEAD%%% - The module line
    %%%WIRES%%% - All the wires and regs needed for the testbench
    %%%UUT%%% - The UUT instance (needs an open parenthesis after it)
    %%%ARGS%%% - The connections to the UUT (needs close parenthesis and semicolon after it)
    %%%PERIOD%%% - The PERIOD parameter
    %%%DUMP%%% - The $dumpfile and $dumpvars directives
    %%%CLOCK%%% - Clock generation code
    %%%RESET%%% - Reset generation code
    %%%INCLUDE%%% - User include string
```

Note you have to provide a few things in the template such as the syntax between the UUT
instance and its arguments. DUMP, and RESET need to be inside initial blocks. I
did change the CLOCK text to use an always block so it would stand alone so that's different from the original code.

The file template.v shows an example custom template

Here is the current default template:
```
    // Auto generatated test bench (internal tbgen.py template)
    %%%TIMESCALE%%%
    %%%HEAD%%%
    %%%WIRES%%%
    %%%UUT%%% (
    %%%ARGS%%% );
    %%%PERIOD%%%
    %%%CLOCK%%%
    initial begin
    %%%DUMP%%%
    end
    initial begin
    %%%RESET%%%
    end
    
    %%%INCLUDE%%%
    
    endmodule
```
			    
