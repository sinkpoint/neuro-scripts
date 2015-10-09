# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 15:36:45 2013

@author: dchen
"""

#!/usr/bin/env python
import sys
from optparse import OptionParser

	
class MncRename:
	def __init__(self, options, args):
		self.options = options
		self.args = args
		
	def go(self):
		fname = self.options.input
  
		f = open(fname)
		data = f.readlines()
		for d in data:
			print(d)
		f.close()



if __name__ == '__main__':
	parser = OptionParser(usage="Usage: %prog <input>")
	parser.add_option("-i", "--input", dest="input", help="File to process")

	(options, args) = parser.parse_args()

	if len(args) != 1:
		parser.print_help()
		sys.exit(2)
	else:
		prog = MncRename(options, args)
		prog.go()

