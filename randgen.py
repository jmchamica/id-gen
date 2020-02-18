#!/usr/bin/python

import sys, random

# Attended in the catch block
generator = None
try:
	# Available values
	formats = [ "plain", "csv", "json" ]
	col_types = [ "name", "firstname", "surname", "email" ]
	emails = [ "@gmail.com", "@outlook.com", "@hotmail.com", "@mail.com", "@yahoo.com" ]
	stderr = sys.stderr
	output = sys.stdout

	# Infinite source of names
	# __next__ returns a dictionary of values to be formatted by this class' implementations
	class RandomTupleGenerator:
		def __init__(self, names, surnames, cols, iterations):
			self.names = names # collection of firstnames to pick from
			self.surnames = surnames # collection of surnames to pick from
			self.cols = cols # column labels
			self.iterations = iterations # maximum iterations. -1 for infinity
			self.idx = 0 # iteration counter
			
			# Prevent collision of unique values
			self.emails = []
					
		def __iter__(self):
			return self
			
		def __next__(self):
			if self.iterations == 0:
				raise StopIteration()

			if self.iterations > 0:
				self.iterations -= 1
			self.idx += 1
			
			attributes = {
				'firstname' : random.choice(self.names),
				'surname' : random.choice(self.surnames)
			}
			attributes.update({'name': "%s %s" % (attributes["firstname"], attributes["surname"])})
			
			# Generate pseudo-random email and check if it already exists
			while True:
				email = "%s%d%s" % (attributes["name"].lower().replace(" ", random.choice([ "", "-", "_" ])), random.randint(0, 999), random.choice(emails))
				
				if self.emails.count(email) == 0:
					self.emails.append(email)
					attributes.update({'email' : email})
					break

			return attributes

	class RandomJsonGenerator(RandomTupleGenerator):
		def __next__(self):
			attributes = RandomTupleGenerator.__next__(self)
	
			elem = "{"
			if self.idx == 1:	
				elem = "[\n{"
			
			for c in self.cols:					
				elem += ' "%s": "%s",' % (c, attributes[c])
			
			elem = elem[:-1] # trim last ","
			elem += " },"
			if self.iterations == 0:
				elem = elem[:-1] + "\n]"
			return elem
			
	class RandomCsvGenerator(RandomTupleGenerator):
		def __next__(self):
			attributes = RandomTupleGenerator.__next__(self)

			elem = ""
			if self.idx == 1:
				elem += ",".join(cols) + "\n"
				
			for c in self.cols:
				elem += '"' + attributes[c] + "\","
			
			return elem[:-1] # trim last ","
					
	class RandomPlainGenerator(RandomTupleGenerator):
		def __next__(self):
			attributes = RandomTupleGenerator.__next__(self)

			elem = ""
			for c in self.cols:
				elem += attributes[c] + " "
				
			return elem[:-1] # trim last " "


	def pick_generator(firstnames, surnames, cols, iterations, outformat):
		if outformat == "json":
			return RandomJsonGenerator(firstnames, surnames, cols, iterations)
		if outformat == "csv":
			return RandomCsvGenerator(firstnames, surnames, cols, iterations)
			
		return RandomPlainGenerator(firstnames, surnames, cols, iterations)


	# Save file contents in a list and close handle ASAP
	def file_to_list(filename):
		f = open(filename, "r", encoding="utf-8")

		arr = []
		for l in f:
			arr.append(l.strip('\n'))

		f.close()
		return arr

	# Properties and arguments' interpretation
	## Defaults
	lang = "us"
	filename = None # default = stdout
	iterations = -1   # default = infinity
	outformat = formats[0]
	cols = [ col_types[0] ]

	for arg in sys.argv:
		pair = arg.split('=')
		if len(pair) != 2:
			continue
		prop  = pair[0]
		value = pair[1]

		if prop == "lang":
			lang = value

		elif prop == "file":
			filename = value

		elif prop == "iter":
			iterations = int(value)

		elif prop == "format":
			if formats.count(value) == 0:
				print("'%s' is not an available format. Using 'plain', instead." % value, file=stderr)
			else:
				outformat = value

		elif prop == "cols":
			mycols = value.split(',')
			ret = []

			for c in mycols:
				if col_types.count(c) == 0:
					print("'%s' is not an available column type. Skipping." % c, file=stderr)
					continue
				ret.append(c)

			if len(ret) > 0:
				cols = ret

	del sys
	
	# Store all names in auxiliar collections
	try:
		firstnames = file_to_list("names/%s/boynames" % lang) + file_to_list("names/%s/girlnames" % lang)
		surnames = file_to_list("names/%s/surnames" % lang)

	except FileNotFoundError:
		print("Language %s is not supported" % lang, file=stderr)
		quit(128)

	# Printing output is stdout (default), or a specified file
	if filename != None:
		output = open(filename, "a", encoding="utf-8")
		
	# Iterate through a random tuple source
	generator = pick_generator(firstnames, surnames, cols, iterations, outformat)
	for l in generator:
		print(l, file=output)
		
	output.close()
except KeyboardInterrupt:
	if generator is not None:
		generator.iterations = 1
		for l in generator:
			print(l, file=output)
		output.close()
	quit(1)
