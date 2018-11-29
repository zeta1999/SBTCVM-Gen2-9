#!/usr/bin/env python

import os
if not os.path.isdir("vmsystem"):
	print("changing to script location...")
	os.chdir(os.path.dirname(os.path.abspath(__file__)))


import vmsystem.libbaltcalc as libbaltcalc
from vmsystem.libbaltcalc import btint
import vmsystem.libtextcon as tcon
import time
import sys
import vmsystem.iofuncts as iofuncts
import vmsystem.g2common as g2com

try:
	import pygame
except ImportError:
	sys.exit("ERROR: pygame not found. (REQUIRED)")
	
	
#just point xrange to range in python3.
vers=sys.version_info[0]
if vers==3:
	xrange=range

def packart_maker(imagepath, notrailnew=0):
	print("converting image...")
	image=pygame.image.load(imagepath)
	xsize=image.get_width()
	ysize=image.get_height()
	#print(image.get_height())
	#print(ysize)
	size=2
	outf=open(imagepath.rsplit(".")[0]+".tas0", 'w')
	outf.write('''#SBTCVM Gen2-9 GFXCON: ternary-packed art conversion.
#image file: ''' + imagepath + "\n")
	outf.write("head-nspin=stdnsp\nfopset1;>io.ttywr\nfopset2;>io.packart\n")
	for coly in xrange(0, ysize):
		buffx=""
		for linex in xrange(0, xsize):
			pixcol = image.get_at((linex, coly))
			level = (pixcol[0] + pixcol[1] + pixcol[2])//3
			if level<85:
				buffx+="-"
			elif level<170:
				buffx+="0"
			else:
				buffx+="+"
			if len(buffx)==9:
				outf.write("fopwri2;" + buffx + "\n")
				size+=1
				buffx=""
		if linex>=81:
			print("WARNING: IMAGE BEYOND MAXIMUM TERNARY PACKED ART WIDTH \n ALLOWED BY PYGAME FRONTEND (81)")
		while len(buffx)<9 and buffx!="":
			buffx+="-"
		if buffx!="":
			outf.write("fopwri2;" + buffx + "\n")
			size+=1
		if coly<ysize-1 or notrailnew==0:
			outf.write("fopwri1;:\\n\n")
		size+=1
		#print(coly)
	outf.close()
	print("Done.")
	print(g2com.nonetformatted_smart(size))
	return

def colart_maker(imagepath, notrailnew=0):
	print("converting image...")
	image=pygame.image.load(imagepath)
	xsize=image.get_width()
	ysize=image.get_height()
	#print(image.get_height())
	#print(ysize)
	size=3
	outf=open(imagepath.rsplit(".")[0]+".tas0", 'w')
	outf.write('''#SBTCVM Gen2-9 GFXCON: ternary-packed art conversion.
#image file: ''' + imagepath + "\n")
	outf.write("head-nspin=stdnsp\nfopset1;>io.ttywr\nfopset2;>io.cpack\n")
	for coly in xrange(0, ysize):
		buffx=""
		for linex in xrange(0, xsize):
			pixcol = image.get_at((linex, coly))
			for level in (pixcol[0], pixcol[1], pixcol[2]):
				if level<85:
					buffx+="-"
				elif level<170:
					buffx+="0"
				else:
					buffx+="+"
			if len(buffx)==9:
				outf.write("fopwri2;" + buffx + "\n")
				size+=1
				buffx=""
		if linex>=81:
			print("WARNING: IMAGE BEYOND MAXIMUM TERNARY PACKED ART WIDTH \n ALLOWED BY PYGAME FRONTEND (81)")
		while len(buffx)<9 and buffx!="":
			buffx+="-"
		if buffx!="":
			outf.write("fopwri2;" + buffx + "\n")
			size+=1
		if coly<ysize-1 or notrailnew==0:
			outf.write("fopwri1;:\\n\n")
		size+=1
		#print(coly)
	outf.write('fopset2;>io.packart\n')
	outf.close()
	print("Done.")
	print(g2com.nonetformatted_smart(size))
	return


if __name__=="__main__":
	try:
		cmd=sys.argv[1]
	except IndexError:
		cmd=None
	try:
		arg=sys.argv[2]
	except IndexError:
		arg=None
	if cmd in ["-h", "--help"]:
		print('''SBTCVM Gen2-9 gfx conversion utility.
-p(n) [image]  : convert an image into 3-color ternary-packed art, and place it in
    a tas0 file. append n for no trailing newline.
-cp(n) [image] : convert an image into 27-color ternary packed art, and place it
    in a tas0 file. append n for no trailing newline.''')
	elif cmd in ["-v", "--version"]:
		print("SBTCVM Gen2-9 gfx conversion utility. v1.0.0\n" + "part of SBTCVM-Gen2-9 v2.1.0.alpha")
	elif cmd in ["-a", "--about"]:
		print('''SBTCVM Gen2-9 gfx conversion utility.
v1.0.0
part of SBTCVM-Gen2-9 (v2.1.0.alpha)

Copyright (c) 2016-2018 Thomas Leathers and Contributors 

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
	elif cmd in ["-p"]:
		print("Ternary-Packed art encoder.")
		packart_maker(iofuncts.findtrom(arg, ext=".png", exitonfail=1, exitmsg="image file was not found. STOP", dirauto=1))
		
	elif cmd in ["-cp"]:
		print("Color Ternary-Packed art encoder.")
		colart_maker(iofuncts.findtrom(arg, ext=".png", exitonfail=1, exitmsg="image file was not found. STOP", dirauto=1))
	elif cmd in ["-pn"]:
		print("Ternary-Packed art encoder.")
		packart_maker(iofuncts.findtrom(arg, ext=".png", exitonfail=1, exitmsg="image file was not found. STOP", dirauto=1), 1)
		
	elif cmd in ["-cpn"]:
		print("Color Ternary-Packed art encoder.")
		colart_maker(iofuncts.findtrom(arg, ext=".png", exitonfail=1, exitmsg="image file was not found. STOP", dirauto=1), 1)
		
	elif cmd == None:
		print("Tip: try gfxcon.py -h for help.")