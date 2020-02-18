#!/usr/bin/python

import sys

table = []
for l in sys.stdin:
	formatted = l.replace('\n', '')
	table.append(formatted)


table_name = "dbo.ExampleTable"

for arg in sys.argv:
	pair = arg.split('=')
	if len(pair) != 2:
		continue
	prop  = pair[0]
	value = pair[1]

	if prop == "table":
		table_name = value
		
del sys

cols = table[0]
lines = "insert into " + table_name + " values("
for l in table[1:]:
	lines +='\n    (' + l + '),'
lines = lines[:-1] + "\n);"

print(lines)

