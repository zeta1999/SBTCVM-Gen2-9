#!/usr/bin/env python
import os
if not os.path.isdir("vmsystem"):
	print("changing to script location...")
	os.chdir(os.path.dirname(os.path.abspath(__file__)))

import vmsystem.libbaltcalc as libbaltcalc
from vmsystem.libbaltcalc import btint
import vmsystem.MEM_G2x_9
import vmsystem.CPU_G2x_9
import vmsystem.IO_G2x_9
import vmsystem.UIO_PYGAME_G2x_9 as UIO
import vmsystem.COMMON_IO_G2x_9 as devcommon
import vmsystem.SBTVDI_IO_G2x_9 as vdi
import vmsystem.SND_G2x_9 as snd
import vmsystem.tdisk1lib as td1
import vmsystem.iofuncts as iofuncts
import time
import sys

from threading import Thread
progrun=0
uiosys=None




try:
	cmd=sys.argv[1]
except:
	cmd=None
try:
	arg=sys.argv[2]
except:
	arg=None
if cmd in ['help', '-h', '--help']:
	print('''SBTCVM Gen2-9 virtual machine. pygame frontend.
help, -h, --help: this help.
   -v, --version: VM version
   -a, --about: about SBTCVM
   [trom/tdsk1], -r [trom/tdsk1], --run [trom/tdsk1]: launch SBTCVM with the selected TROM/tdsk1 (disk) image
      loaded into memory.
   -s [trom/tdsk1] {CPU speed in Hz}, --slow [trom/tdsk1] {CPU speed in Hz}:
      -s overrides the default CPU clock speed. You may specify a float/int Hz value
      (after the trom/tdsk1 filename). defaults to 2Hz''')
elif cmd in ["-a", "--about"]:
	print('''SBTCVM Gen2-9 virtual machine. pygame frontend.
v2.1.0.alpha

Copyright (c) 2016-2020 Thomas Leathers and Contributors 

see readme.md for more information and licensing of media.

  SBTCVM Gen2-9 is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  SBTCVM Gen2-9 is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with SBTCVM Gen2-9. If not, see <http://www.gnu.org/licenses/>
  
  ''')
elif cmd in ['-v', '--version']:
	print('v2.1.0.alpha')
else:
	
	slow=0
	if cmd==None:
		#romfile='TESTSHORT.TROM'
		romfile='VDIBOOT'
	elif cmd in ['-r', '--run']:
		if arg==None:
			sys.exit("Error! Must specify trom to run!")
		romfile=arg
	elif cmd in ['-s', '--slow']:
		if arg==None:
			sys.exit("Error! Must specify trom to run!")
		romfile=arg
		slow=1
		try: 
			targspeed=float(sys.argv[3])/1000.0
			slowspeed=1/(targspeed*1000.0)
		except IndexError:
			print("Using default slow delay. (2 hz)")
			targspeed=2/1000.0
			slowspeed=1/(targspeed*1000.0)
		except ValueError:
			sys.exit("Error. please specify slow delay as float or int.")
	elif cmd.startswith("-"):
		print("Unknown option: '" + cmd + "' try pyg_sbtcvm.py -h for help.") 
		sys.exit()
	else:
		romfile=cmd
	if slow==1:
		targtime=slowspeed
	else:
		#targspeed is in khz. acuracy may vary.
		targspeed=6.5#approx. speed should be close.
		#calculate approx speed.
		targtime=1/(targspeed*1000.0)
	print("SBTCVM Generation 2 9-trit VM, v2.1.0.alpha\n")
	
	windowprefix=romfile
	diska=None
	diskfile=iofuncts.findtrom(romfile, ext=".tdsk1", exitonfail=0, dirauto=1)
	if diskfile!=None:
		retval=td1.loaddisk(diskfile, readonly=0)
		windowprefix=retval.label
		if not isinstance(retval, str):
			diska=retval
			romfile='VDIBOOT'
			
	#initialize memory subsystem
	memsys=vmsystem.MEM_G2x_9.memory(romfile)
	#initialize IO subsystem
	iosys=vmsystem.IO_G2x_9.io()
	
	cpusys=vmsystem.CPU_G2x_9.cpu(memsys, iosys)
	devcommon.factorydevs(iosys)
	#init SBTVDI interface.
	vdi.sbtvdi(iosys, cpusys, memsys, diska=diska)
	progrun=1
	
	#start sound system
	snd.initsnd(iosys)
	#uio startup
	uiosys = UIO.uio(cpusys, memsys, iosys, windowprefix)
	uiosys.ttyraw("SBTCVM Pygame frontend. SBTCVM Gen2-9 v2.1.0")
	uiosys.ttyraw("ready.")
	dispthr=Thread(target = uiosys.statup, args = [])
	dispthr.daemon=True
	dispthr.start()
	#main loop
	clcnt=0.0
	starttime=time.time()
	while progrun:
		#CPU Parse
		retval=cpusys.cycle()
		#increment clock tick.
		clcnt+=1
		#project when the next cycle should start, then subtract current time.
		xtime=(starttime + (clcnt - 1.0) * targtime) - time.time()
		#sleep for remaining time (xtime) if it is above 0
		if xtime>0.0:
			time.sleep(xtime)
		#exit code:
		elif retval!=None:
			#benchmark session first, as uiosys.powoff() has to wait for the statup thread to terminate.
			#(Store text in variables, as they need to be printed after curses has been shut down.
			postout1=("VMSYSHALT " + str(retval[1]) + ": " + retval[2])
			postout2=("Approx. Speed: '" + str((float(clcnt)/(time.time()-starttime))/1000) + "' KHz")
			postout3=("Target Speed : '" + str(targspeed) + "' Khz")
			
			print(postout1)
			print(postout2)
			print(postout3)
			uiosys.powoff()
			progrun=0
