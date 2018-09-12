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
import argparse

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
        self.otext=""
        
        if vfile_name == None:
            sys.stderr.write("ERROR: You did not provide an input file name.\n")
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
                    print("You did not specify an output file name, using '%s'." % ofname)
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
        if self.otext=="":
            self.otext=self.get_def_template()
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
        
        
#        self.printo( "%s uut (\n" % self.mod_name )
        tmp="%s uut\n" % self.mod_name
        self.otext=re.sub(r"%%%UUT%%%",tmp,self.otext)
        align_cont = self.align_print(list(map(lambda x:("", "." + x[1], "(", x[1], '),'), self.pin_list)), 4)
        align_cont = align_cont[:-2] + "\n"

#        self.printo( align_cont )
        self.otext=re.sub(r"%%%ARGS%%%",align_cont,self.otext)
#        self.printo( ");\n" )
        
    def print_wires(self):
        tmp=self.align_print(list(map(lambda x:(x[3], x[2], x[1], '=0;' if x[3]=='reg' else ';'), self.pin_list)), 4)
        tmp+="\n"
        self.otext=re.sub(r"%%%WIRES%%%",tmp,self.otext)
    
    def print_clock_gen(self,period,dfile,depth,resetpol):
        fsdb = "\t$dumpfile(\"%s\");\n\t$dumpvars(%d, tb_%s);" % (dfile, depth, self.mod_name)
        self.otext=re.sub(r"%%%DUMP%%%",fsdb,self.otext)

        tmp="parameter PERIOD=%d;" % period
        self.otext=re.sub(r"%%%PERIOD%%%",tmp,self.otext)
        clock_gen_text = re.sub('CLK',self.clock_name,"always\n\t#(PERIOD/2) CLK = ~CLK;")
#        self.printo(re.sub('CLK', self.clock_name, clock_gen_text))
        self.otext=re.sub(r"%%%CLOCK%%%",clock_gen_text,self.otext)
        if self.reset_name!="":
            clock_gen_text = "\tRST=1'b%d;\n\t#(PERIOD*2) RST=~RST;\n\t#PERIOD RST=~RST;" % resetpol
#            self.printo(re.sub('RST',self.reset_name, clock_gen_text))
            tmp=re.sub('RST',self.reset_name,clock_gen_text)
            self.otext=re.sub(r"%%%RESET%%%",tmp,self.otext)
        
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

    def print_module_head(self,timescale):
        self.otext=re.sub(r"%%%TIMESCALE%%%","`timescale %s" % timescale, self.otext)
        self.otext=re.sub(r"%%%HEAD%%%","module tb_%s;" % self.mod_name,self.otext)
        
    def print_module_end(self,iname):
        if iname is None:
            iname='user.tb_%s.v' % self.mod_name
#        self.printo("`include \"%s\"\nendmodule\n" % iname)
        self.otext=re.sub(r"%%%INCLUDE%%%","`include \"%s\"" % iname,self.otext)


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

    def set_template(self, fn):
        with open(fn,'r') as tFile:
            self.otext=tFile.read()

    def dump_template(self):
        self.printo(self.get_def_template())
        
    def get_def_template(self):
        return "\
// Auto generatated test bench (internal tbgen.py template)\n\
%%%TIMESCALE%%%\n\
%%%HEAD%%%\n\
%%%WIRES%%%\n\
%%%UUT%%% (\n\
%%%ARGS%%% );\n\
%%%PERIOD%%%\n\n\
%%%CLOCK%%%\n\n\
initial begin\n\
%%%DUMP%%%\n\
end\n\n\
initial begin\n\
%%%RESET%%%\n\
end\n\
\n\
%%%INCLUDE%%%\n\
\n\
endmodule\n\
"
    def write_template(self):
        self.printo("%s" % self.otext)

if __name__ == "__main__":
    print('''***************** tbgen - Auto generate a testbench. *****************
Author: Xiongfei(Alex) Guo <xfguo@credosemi.com>
License: Beerware
''')
    ofile_name = None
        
    aparse = argparse.ArgumentParser(description='Automatically generate Verilog testbench')
    aparse.add_argument('input_file',  help='input Verilog file')
    aparse.add_argument('output_file', help='output Verilog testbench', nargs='?', default=None)
    aparse.add_argument('-p','--period', type=int, help='set period in clock ticks (default=10)', default=10)
    aparse.add_argument('-t','--timescale',help='set timescale (default=1ns/10ps)', default='1ns/10ps')
    aparse.add_argument('-d','--dumpfile',help='set dumpfile (default=tb_output.vcd)', default='tb_output.vcd')
    aparse.add_argument('-l','--level', type=int, help='set dump depth level (usually 0,1, or 2; default=2)', default=2)
    aparse.add_argument('-r','--resetneg', help='set reset to negative (default positive)', action='store_const', const=1, default=0)
    aparse.add_argument('-i','--include', help='sets user include file name (default=user.tb_<name>.v)', default=None)
    aparse.add_argument('-T','--template', help='sets template (default=use internal template; -T ? will dump internal template and exit -- requires dummy input name)', default=None)
    args = aparse.parse_args()

    tbg = TestbenchGenerator(args.input_file, args.output_file)

    if args.template=='?':
        tbg.dump_template();
        sys.exit(1);

    if args.template is not None:
        tbg.set_template(args.template);
    tbg.print_module_head(args.timescale)
    tbg.print_wires()
    tbg.print_dut()
    tbg.print_clock_gen(args.period,args.dumpfile,args.level,args.resetneg)
    tbg.print_module_end(args.include)
    tbg.write_template()
    tbg.close()

