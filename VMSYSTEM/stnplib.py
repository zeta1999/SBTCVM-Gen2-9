#!/usr/bin/env python
from . import libbaltcalc
btint=libbaltcalc.btint
import os
import sys
#from subprocess import call
from . import libtextcon as tcon
from . import g2asmlib
#variable type constants
nptype_int=2
nptype_str=3
nptype_label=4


#SSTNPL compiler main routine library.

stnpvers='v0.2.0'
versint=(0, 2, 0)

class npvar:
	def __init__(self, vname, vdata, vtype=nptype_int):
		self.vname=vname
		self.vdata=vdata
		#future proofing
		self.vtype=vtype

tritvalid="+0-pn"
varvalid="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_1234567890"
reservednames=[""]
class in_var:
	def __init__(self):
		self.keywords=["var"]
	def p0(self, args, keyword, lineno):
		argsplit=args.split("=", 1)
		
		if len(argsplit)!=2:
			return 1, "must specify varname=valiue! '" + str(lineno) + "'"
		data=argsplit[1]
		name=argsplit[0]
		for char in name:
			if char not in varvalid:
				return 1, keyword+": Line: " + str(lineno) + ": Invalid character in variable name! '" + char + "'"
		if name in reservednames:
			return 1, keyword+": Line: " + str(lineno) + ": variable name: '" + args + "' Is reserved."
		if data.startswith("10x"):
			try:
				int(data[3:])
			except ValueError:
				return 1, keyword+": Line: " + str(lineno) + ": decimal int syntax error!"
		#this syntax will make this var equal the encoding data of the specified character.
		if data.startswith(":"):
			if len(data)<2:
				return 1, keyword+": Line: " + str(lineno) + ": Must specify character"
		else:
			if len(data)>9:
				return 1, keyword+": Line: " + str(lineno) + ": string too large!"
			for char in data:
				
				if char not in tritvalid:
					return 1, keyword+": Line: " + str(lineno) + ": invalid char in ternary data string!"
		return 0, None
	def p1(self, args, keyword, lineno):
		argsplit=args.split("=", 1)
		name=argsplit[0]
		data=argsplit[1]
		return [npvar(name, data, vtype=nptype_int)]
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		return 0, None
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		return



class in_val:
	def __init__(self):
		self.keywords=["val"]
	def p0(self, args, keyword, lineno):
		if args.startswith("10x"):
			try:
				int(args[3:])
			except ValueError:
				return 1, keyword+": Line: " + str(lineno) + ": decimal int syntax error!"
			
		else:
			if len(args)>9:
				return 1, keyword+": Line: " + str(lineno) + ": string too large!"
			for char in args:
				
				if char not in tritvalid:
					return 1, keyword+": Line: " + str(lineno) + ": invalid char in ternary data string!"
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		return 0, None
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		destobj.write("#val (used with set to change variable value during runtime.)\nsetreg1;" + args + "\n")
		return
class in_label:
	def __init__(self):
		self.keywords=["label"]
	def p0(self, args, keyword, lineno):
		for char in args:
			if char not in varvalid:
				return 1, keyword+": Line: " + str(lineno) + ": Invalid character in label! '" + char + "'"
		if args in reservednames:
			return 1, keyword+": Line: " + str(lineno) + ": label name: '" + args + "' Is reserved."
		return 0, None
	def p1(self, args, keyword, lineno):
		return [npvar(args, None, vtype=nptype_label)]
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		return 0, None
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		destobj.write("#label\n" + "null;;" + args+"--label" + "\n")
		return


class in_rawasm:
	def __init__(self):
		self.keywords=["a", "asm"]
	def p0(self, args, keyword, lineno):
		print("Embedded assembly code at line: '" + str(lineno) + "': " + args)
		return 0, None
	def p1(self, args, keyword, lineno):
		return [npvar(args, None, vtype=nptype_label)]
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		return 0, None
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		destobj.write("#___RAW ASSEMBLY CODE___\n#_______NOTE: this corresponds to SSTNPL source line #" + str(lineno) + "\n" + args + "\n")
		return

class in_intcommon1:
	def __init__(self, keywords, prearg, postarg, comment):
		self.keywords=keywords
		self.prearg=prearg
		self.postarg=postarg
		self.comment=comment
	def p0(self, args, keyword, lineno):
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		if args in valid_nvars:
			return 0, None
		else:
			return 1, keyword+": Line: " + str(lineno) + ": Nonexistant variable'" + args + "'"
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		destobj.write("#" + self.comment + "\n" + self.prearg + args + self.postarg)
		return
		

class in_invert:
	def __init__(self):
		self.keywords=["invert"]
		self.comment="invert a variable."
	def p0(self, args, keyword, lineno):
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		if args in valid_nvars:
			return 0, None
		else:
			return 1, keyword+": Line: " + str(lineno) + ": Nonexistant variable'" + args + "'"
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		destobj.write("#" + self.comment + "\ndataread1;>" + args + "\ninvert1\ndatawrite1;>" + args + "\n")
		return

class in_getchar:
	def __init__(self):
		self.keywords=["getchar"]
		self.comment="Get character from TTY input."
	def p0(self, args, keyword, lineno):
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		if args in valid_nvars:
			return 0, None
		else:
			return 1, keyword+": Line: " + str(lineno) + ": Nonexistant variable'" + args + "'"
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		destobj.write("#" + self.comment + "\nioread1;>io.ttyrd\ndatawrite1;>" + args + "\n")
		return


class in_labelgoto:
	def __init__(self):
		self.keywords=["goto", "gsub"]
	def p0(self, args, keyword, lineno):
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		if args in labels:
			return 0, None
		else:
			return 1, keyword+": Line: " + str(lineno) + ": Nonexistant label'" + args + "'"
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		if keyword=="gsub":
			
			destobj.write("#goto (extra code stores away return address.)\n" + "setreg1;>goto--jumper-" +  str(lineno) + "\ns1push1\ngoto;>" + args +"--label" + "\nnull;;goto--jumper-" +  str(lineno) + "\n")
		else:
			destobj.write("#goto \n" + "goto;>" + args +"--label" + "\n")
		return

class in_condgoto:
	def __init__(self, keywords, gotoop):
		self.keywords=keywords
		self.gotoop=gotoop
	def p0(self, args, keyword, lineno):
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		arglist=args.split(" ")
		if len(arglist)!=3:
			if len(arglist)!=2:
				return 1, keyword+": Line: " + str(lineno) + ": Must specify args as '<var>,<var> goto <label>'"
			#return mode doesn't need label argument.
			elif arglist[1]!="return":
				return 1, keyword+": Line: " + str(lineno) + ": Must specify args as '<var>,<var> goto <label>'"
		#check label for goto and gsub
		if len(arglist)==3:
			label=arglist[2]
			if not label in labels:
				return 1, keyword+": Line: " + str(lineno) + ": Nonexistant label'" + label + "'"
		#check goto mode
		if arglist[1] not in ["goto", "gsub", "return"]:
			return 1, keyword+": Line: " + str(lineno) + ": Invalid goto mode! must be 'goto', 'gsub', or 'return'"
		#variable check
		for x in arglist[0].split(","):
			if not x in valid_nvars:
				return 1, keyword+": Line: " + str(lineno) + ": Nonexistant variable'" + x + "'"
		return 0, None
		

	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		arglist=args.split(" ")
		if len(arglist)==3:
			label=arglist[2]
		
		var0, var1 = arglist[0].split(",")
		if arglist[1]=="gsub":
			destobj.write('''#conditional subroutine goto
dataread1;>''' + var0 + '''
dataread2;>''' + var1 + '''
''' + self.gotoop + ''';>goto--branch-''' + str(lineno) + '''
goto;>goto--jumper-''' +  str(lineno) + '''
setreg1;>goto--jumper-''' +  str(lineno) + ";goto--branch-" +  str(lineno) + "\ns1push1\ngoto;>" + label + "--label\nnull;;goto--jumper-" +  str(lineno) + "\n")
		elif arglist[1]=="return":
			destobj.write('''#conditional return
dataread1;>''' + var0 + '''
dataread2;>''' + var1 + '''
''' + self.gotoop + ''';>goto--branch-''' + str(lineno) + '''
goto;>goto--jumper-''' +  str(lineno) + '''
s1pop1;''' + ";goto--branch-" +  str(lineno) + "\ngotoreg1\nnull;;goto--jumper-" +  str(lineno) + "\n")
		else:
			destobj.write('''#conditional goto
dataread1;>''' + var0 + '''
dataread2;>''' + var1 + '''
''' + self.gotoop + ''';>goto--branch-''' + str(lineno) + '''
goto;>goto--jumper-''' +  str(lineno) + '''
setreg1;>goto--jumper-''' +  str(lineno) + ";goto--branch-" +  str(lineno) + "\ngoto;>" + label + "--label\nnull;;goto--jumper-" +  str(lineno) + "\n")
		return

class in_int2opmath:
	def __init__(self, keywords, instruct, comment):
		self.keywords=keywords
		self.instruct=instruct
		self.comment=comment
	def p0(self, args, keyword, lineno):
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		argsplit=args.split(",")
		if len(argsplit)!=2:
			return 1, keyword+": Line: " + str(lineno) + ": Two comma-separated variable arguments required!"
		for argx in argsplit:
			if argx in valid_nvars:
				return 0, None
			else:
				return 1, keyword+": Line: " + str(lineno) + ": Nonexistant variable'" + argx + "'"
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		arg0, arg1 = args.split(",")
		destobj.write("#" + self.comment + "\ndataread1;>" + arg0 + "\ndataread2;>" + arg1 + "\n" + self.instruct)
		return


class in_int2opswap:
	def __init__(self):
		self.keywords=["swap"]
	def p0(self, args, keyword, lineno):
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		argsplit=args.split(",")
		if len(argsplit)!=2:
			return 1, keyword+": Line: " + str(lineno) + ": Two comma-separated variable arguments required!"
		for argx in argsplit:
			if argx in valid_nvars:
				return 0, None
			else:
				return 1, keyword+": Line: " + str(lineno) + ": Nonexistant variable'" + argx + "'"
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		arg0, arg1 = args.split(",")
		destobj.write("#swap variables \ndataread1;>" + arg0 + "\ndataread2;>" + arg1 + "\ndatawrite1;>" + arg1 + "\ndatawrite2;>" + arg0 + "\n")
		return
	

class in_int2opcopy:
	def __init__(self):
		self.keywords=["copy"]
	def p0(self, args, keyword, lineno):
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		argsplit=args.split(",")
		if len(argsplit)!=2:
			return 1, keyword+": Line: " + str(lineno) + ": Two comma-separated variable arguments required!"
		for argx in argsplit:
			if argx in valid_nvars:
				return 0, None
			else:
				return 1, keyword+": Line: " + str(lineno) + ": Nonexistant variable'" + argx + "'"
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		arg0, arg1 = args.split(",")
		destobj.write("#copy variables \ndataread1;>" + arg0 + "\ndatawrite1;>" + arg1 + "\n")
		return


class in_common0:
	def __init__(self, keywords, xcode, comment):
		self.keywords=keywords
		self.xcode=xcode
		self.comment=comment
	def p0(self, args, keyword, lineno):
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		return 0, None
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		destobj.write("#" + self.comment + "\n" + self.xcode)
		return
		




class in_print:
	def __init__(self):
		self.keywords=["print", "prline"]
		self.comment="print"
	def p0(self, args, keyword, lineno):
		for char in args:
			if char not in tcon.normal_char_list:
				return 1, keyword+": Line: " + str(lineno) + ": invalid character'" + char + "'"
		return 0, None
	def p1(self, args, keyword, lineno):
		return []
	def p2(self, args, keyword, lineno, nvars, valid_nvars, labels):
		return 0, None
	def p3(self, args, keyword, lineno, nvars, valid_nvars, labels, destobj):
		destobj.write("#" + self.comment + "\n")
		
		for char in args:
			destobj.write("fopwri1;:" + tcon.chartoasmchar[char] + "\n")
		if keyword=="prline":
			destobj.write("fopwri1;:\\n\n")
		return


def headinfo(filename, basename):
	return '''#SSTNPL COMPILER ''' + stnpvers + '''
#header
head-rname=''' + basename + '''
head-nspin=stdnsp
fopset1;>io.ttywr
#stnp source file: (autogenerated from) "''' + filename + '''
'''

def compwrap(sourcepath):
	##SSTNPL compile procedure function.
	
	basepath=sourcepath.rsplit(".", 1)[0]
	bpdir=os.path.dirname(basepath)
	bpname=os.path.basename(basepath)
	asmname=bpname
	
	#open source file and init mainloop class
	if asmname.startswith("auto_"):
		asmname="x_" + asmname
	destpath=os.path.join(bpdir, asmname + "__stnp.tasm")
	sourcefile=open(sourcepath, 'r')
	print("SSTNPL COMPILER STARTUP:")
	mainl=mainloop(sourcefile, destpath, sourcepath, bpname)
	print("Pass 0: first syntax check")
	mainret=mainl.p0()
	if mainret[0]==1:
		sys.exit(mainret[1])
	print("Pass 1: variable pass")
	mainl.p1()
	print("Pass 2: second syntax check (with variables)")
	mainret=mainl.p2()
	if mainret[0]==1:
		sys.exit(mainret[1])
	print("Pass 3: compile pass")
	mainl.p3()
	print("autorunning assembler:")
	#call(['python',  'g2asm.py', destpath])
	#call assembler's wrapper function.
	g2asmlib.assemble(destpath, syntaxonly=0, pfx=("g2asm:   "))
	return


class mainloop:
	def __init__(self, srcobj, destpath, sourcepath, bpname):
		self.filename=sourcepath
		self.srcobj=srcobj
		self.outobj=open(destpath, "w")
		self.destpath=destpath
		self.nvars=[]
		self.valid_nvars=[]
		self.instructs=[in_var(),
		in_label(),
		in_intcommon1(["dumpt"], "dataread1;>", "\niowrite1;>io.tritdump\n", "Dump (trits)"),
		in_intcommon1(["chardump"], "dataread1;>", "\niowrite1;>io.ttywr\n", "Dump (character)"),
		in_intcommon1(["set", "set1"], "datawrite1;>", "\n", "set(1) (used after 2-op math, asm code, or get)"),
		in_intcommon1(["get", "get1"], "dataread1;>", "\n", "get(1) (may be used with set, or asm code)"),
		in_intcommon1(["set2"], "datawrite2;>", "\n", "set2 (used for asm, or get2)"),
		in_intcommon1(["get2"], "dataread2;>", "\n", "get2 (may be used with set2, and asm code.)"),
		in_int2opmath(["add"], "add\n", "add (2op math)"),
		in_int2opmath(["sub"], "sub\n", "subtract (2op math)"),
		in_int2opmath(["div"], "div\n", "divide (2op math)"),
		in_int2opmath(["mul"], "mul\n", "multiply (2op math)"),
		in_labelgoto(), 
		in_int2opcopy(),
		in_int2opswap(),
		in_val(),
		in_invert(),
		in_print(),
		in_rawasm(),
		in_getchar(),
		in_condgoto(["if"], "gotoif"),
		in_condgoto(["ifmore"], "gotoifmore"),
		in_condgoto(["ifless"], "gotoifless"),
		in_common0(["return"], "s1pop1\ngotoreg1\n", "return from subroutine."),
		in_common0(["newline"], "fopwri1;:\\n\n", "print newline"),
		in_common0(["space"], "fopwri1;:\\s\n", "print space"),
		in_common0(["stop"], "stop\n", "stop (shutdown vm)"),
		in_intcommon1(["dumpd"], "dataread1;>", "\niowrite1;>io.decdump\n", "Dump (decimal)")]
		self.bpname=bpname
		self.labels=[]
	def p0(self):
		self.srcobj.seek(0)
		lineno=0
		for line in self.srcobj:
			lineno+=1
			if line.endswith("\n"):
				line=line[:-1]
			if '#' in line:
				line=line.rsplit("#", 1)[0]
			try:
				keyword, data = line.split(" ", 1)
			except ValueError:
				keyword = line
				data=""
			for inst in self.instructs:
				if keyword in inst.keywords:
					retval, errordesc = inst.p0(data, keyword, lineno)
					if retval!=0:
						return 1, errordesc
		return 0, None
	def p1(self):
		self.srcobj.seek(0)
		lineno=0
		for line in self.srcobj:
			lineno+=1
			if line.endswith("\n"):
				line=line[:-1]
			if '#' in line:
				line=line.rsplit("#", 1)[0]
			try:
				keyword, data = line.split(" ", 1)
			except ValueError:
				keyword = line
				data=""
			for inst in self.instructs:
				if keyword in inst.keywords:
					retvars = inst.p1(data, keyword, lineno)
					for rvar in retvars:
						if rvar.vtype==nptype_int:
							self.valid_nvars.extend([rvar.vname])
							self.nvars.extend([rvar])
						if rvar.vtype==nptype_label:
							self.labels.extend([rvar.vname])
	def p2(self):
		self.srcobj.seek(0)
		lineno=0
		for line in self.srcobj:
			lineno+=1
			if line.endswith("\n"):
				line=line[:-1]
			if '#' in line:
				line=line.rsplit("#", 1)[0]
			try:
				keyword, data = line.split(" ", 1)
			except ValueError:
				keyword = line
				data=""
			for inst in self.instructs:
				if keyword in inst.keywords:
					retval, errordesc = inst.p2(data, keyword, lineno, self.nvars, self.valid_nvars, self.labels)
					if retval!=0:
						return 1, errordesc
		return 0, None
	def p3(self):
		self.outobj.write(headinfo(self.filename, self.bpname))
		for rvar in self.nvars:
			if rvar.vtype==nptype_int:
				self.outobj.write('null;' + rvar.vdata + ';' + rvar.vname + "\n")
		self.srcobj.seek(0)
		lineno=0
		for line in self.srcobj:
			lineno+=1
			if line.endswith("\n"):
				line=line[:-1]
			if '#' in line:
				line=line.rsplit("#", 1)[0]
			try:
				keyword, data = line.split(" ", 1)
			except ValueError:
				keyword = line
				data=""
			for inst in self.instructs:
				if keyword in inst.keywords:
					inst.p3(data, keyword, lineno, self.nvars, self.valid_nvars, self.labels, self.outobj)
					
		self.outobj.write("#END OF FILE\n")
		self.outobj.close()
	
	