#! /usr/bin/python

# THE BEER-WARE LICENSE" (Revision 42):
# <xfguo@xfguo.org> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Xiongfei(Alex) Guo.

# some minor additions by Al Williams 2018-9-11

'''
Created on 2010-4-23

@author: Alex Guo
'''

import re
import sys

class TestbenchGenerator(object):
    '''
    verilog test bench auto generation
    '''

    def __init__(self, vfile_name = None, ofile_name = None):
        self.vfile_name = vfile_name
        self.vfile = None
        self.ofile_name = ofile_name
        if(ofile_name == None):
            self.ofile = sys.stdout
        self.vcont = ""
        self.mod_name = ""
        self.pin_list = []
        self.clock_name = 'clk'
        self.reset_name = 'rst'
        
        if vfile_name == None:
            sys.stderr.write("ERROR: You aren't specfic a input file name.\n")
            sys.exit(1)
        else:
            self.open()
        self.parser()
        self.open_outputfile()

    def open(self, vfile_name = None):
        if vfile_name != None:
            self.vfile_name = vfile_name
            
        try:
            self.vfile = open(self.vfile_name, 'r')
            self.vcont = self.vfile.read() 
        except Exception as e:
            print("ERROR: Input file error.\n ERROR:    %s" % e)
            sys.exit(1)
            
    def open_outputfile(self, ofile_name = None):
        try:
            if(ofile_name == None):
                if(self.ofile_name == None):
                    ofname = "tb_%s.v" % self.mod_name
                    self.ofile = open(ofname, 'w')
                    print("Your did not specify an output file name, use '%s' instead." % ofname)
                else:
                    self.ofile = open(self.ofile_name, 'w')
                    print("Output file is '%s'." % self.ofile_name)
            else:
                self.ofile = open(ofile_name, 'w')
                print "Output file is '%s'." % ofile_name
        except Exception as e:
            print("ERROR: Output file error. \n ERROR:    %s" % e)
            sys.exit(1)
                
    def clean_other(self, cont):
        ## clean '// ...'
        cont = re.sub(r"//[^\n^\r]*", '\n', cont)
        ## clean '/* ... */'
        cont = re.sub(r"/\*.*\*/", '', cont)
        ## clean '`define ..., etc.'
        #cont = re.sub(r"[^\n^\r]+`[^\n^\r]*", '\n', cont)
        ## clean tables
        cont = re.sub(r'    +', ' ', cont)
        ## clean '\n' * '\r'
        #cont = re.sub(r'[\n\r]+', '', cont)
        return cont
        
    def parser(self):
        print("Parsing...")
        # print vf_cont 
        mod_pattern = r"module[\s]+(\S*)[\s]*\([^\)]*\)[\s\S]*"  
        
        module_result = re.findall(mod_pattern, self.clean_other(self.vcont))
        #print module_result
        self.mod_name = module_result[0]
        
        self.parser_inoutput()
        self.find_clk_rst()
             
    
    def parser_inoutput(self):
        pin_list = self.clean_other(self.vcont) 
        
        comp_pin_list_pre = []
        for i in re.findall(r'(input|output|inout)[\s]+([^;,\)]+)[\s]*[;,]', pin_list):
            comp_pin_list_pre.append((i[0], re.sub(r"^reg[\s]*", "", i[1])))
            
        comp_pin_list = []
        type_name = ['reg', 'wire', 'wire', "ERROR"]
        for i in comp_pin_list_pre:
            x = re.split(r']', i[1])
            type = 0;
            if i[0] == 'input':
                type = 0
            elif i[0] == 'output':
                type = 1
            elif i[0] == 'inout':
                type = 2
            else:
                type = 3

            if len(x) == 2:
                x[1] = re.sub('[\s]*', '', x[1])
                comp_pin_list.append((i[0], x[1], x[0] + ']', type_name[type]))
            else:
                comp_pin_list.append((i[0], x[0], '', type_name[type]))
        
        self.pin_list = comp_pin_list
        # for i in self.pin_list: print i
        
    def print_dut(self):
        max_len = 0
        for cpin_name in self.pin_list:
            pin_name = cpin_name[1]
            if len(pin_name) > max_len:
                max_len = len(pin_name)
        
        
        self.printo( "%s uut (\n" % self.mod_name )
        
        align_cont = self.align_print(list(map(lambda x:("", "." + x[1], "(", x[1], '),'), self.pin_list)), 4)
        align_cont = align_cont[:-2] + "\n"
        self.printo( align_cont )
        
        self.printo( ");\n" )
        
    def print_wires(self):
        self.printo(self.align_print(list(map(lambda x:(x[3], x[2], x[1], ';'), self.pin_list)), 4))
        self.printo("\n")
    
    def print_clock_gen(self):
        fsdb = "    $dumpfile(\"db_tb_%s.vcd\");\n    $dumpvars(2, tb_%s);\n" % (self.mod_name, self.mod_name)

        clock_gen_text = "\nparameter PERIOD = 10; //adjust for your timescale\n\ninitial begin\n%s    CLK = 1'b0;\n    #(PERIOD/2);\n    forever\n        #(PERIOD/2) CLK = ~CLK;\nend\n" % fsdb
        self.printo(re.sub('CLK', self.clock_name, clock_gen_text))
        if self.reset_name!="":
            clock_gen_text = "\ninitial begin // invert if reset is negative\n        RST=1'b0;\n         #(PERIOD*2) RST=~RST;\n         #PERIOD RST=~RST;\n         end\n"
            self.printo(re.sub('RST',self.reset_name, clock_gen_text))
        
    def find_clk_rst(self):
        for pin in self.pin_list:
            if re.match(r'[\S]*(clk|clock)[\S]*', pin[1]):
                self.clock_name = pin[1]
                print("Clock signal detected: '%s'." % pin[1])
                break

        for pin in self.pin_list:
            if re.match(r'rst|reset', pin[1]):
                self.reset_name = pin[1]
                print("Reset signal detected: '%s'." % pin[1])
                break

    def print_module_head_orig(self):
        self.printo("`include \"timescale.v\"\nmodule tb_%s;\n\n" % self.mod_name)

    def print_module_head(self):
        self.printo("`timescale 1ns/100ps //Adjust to suit\n\nmodule tb_%s;\n\n" % self.mod_name)
        
    def print_module_end(self):
        self.printo("`include \"user.tb_%s.v\"\nendmodule\n" % self.mod_name)

    def printo(self, cont):
        self.ofile.write(cont)

    def close(self):
        if self.vfile != None:
            self.vfile.close()
        print("Output complete.\n\n")

    def align_print(self, content, indent):
        """ Align pretty print."""

        row_len = len(content)
        col_len = len(content[0])
        align_cont = [""] * row_len
        for i in range(col_len):
            col = list(map(lambda x:x[i], content))
            max_len = max(list(map(len, col)))
            for i in range(row_len):
                l = len(col[i])
                align_cont[i] += "%s%s" % (col[i], (indent + max_len - l) * ' ')
        
        # remove space in line end
        align_cont = list(map(lambda s:re.sub('[ ]*$', '', s), align_cont))
        return "\n".join(align_cont) + "\n"
        

if __name__ == "__main__":
    print('''***************** tbgen - Auto generate a testbench. *****************
Author: Xiongfei(Alex) Guo <xfguo@credosemi.com>
License: Beerware
''')
    ofile_name = None
    if len(sys.argv) == 1:
        sys.stderr.write("ERROR: You aren't specfic a input file name.\n")
        print("Usage: tbgen input_verilog_file_name [output_testbench_file_name]")
        sys.exit(1)
    elif len(sys.argv) == 3:
        ofile_name = sys.argv[2]
        
    tbg = TestbenchGenerator(sys.argv[1], ofile_name)

    tbg.print_module_head()
    tbg.print_wires()
    tbg.print_dut()
    tbg.print_clock_gen()
    tbg.print_module_end()
    tbg.close()

