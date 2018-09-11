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
4. Put an include for you user-generated code. This is important because if you change the generated file and regenerate it, you'll lose your changes.
5. Changed $dumpvars to level 2
6. Added a simple example

Nothing major, and -- of course -- this is just a template to get you started but don't forget
that any changes you make will be clobbered if you regenerate the testbench!

Example
-------

    python tbgen.py top.v top.tb.v
    iverilog top.tb.v top.v -o top
    vvp top
    gtkwave db_tb_top.vcd

Or try http://edaplayground.com if you don't want to install iverilog and gtkwave.
