#!/usr/lib/python2.7

# DIAMOND_specific_organism_retriever.py
# Created 1/30/17, by Sam Westreich

# Purpose: This takes a DIAMOND outfile and the RefSeq database and pulls out hits to any specific organism, identifying the raw input reads that were mapped to that organism.

# Bad usage:
# -I		infile
# -SO		specific target organism
# -D		database file

# imports
import operator, sys, time, gzip, re

# String searching function:
def string_find(usage_term):
	for idx, elem in enumerate(sys.argv):
		this_elem = elem
		next_elem = sys.argv[(idx + 1) % len(sys.argv)]
		if elem == usage_term:
			 return next_elem

# loading starting file
if "-I" in sys.argv:
	infile_name = string_find("-I")
else:
	sys.exit ("WARNING: infile must be specified using '-I' flag.")

# optional outfile of specific organism results
if "-SO" in sys.argv:
	target_org = string_find("-SO")
	target_org_outfile = open(infile_name[:-5] + "_" + target_org + ".tsv", "w")
else:
	sys.exit("Need to specify target organism with -SO flag.")

# loading database file
if "-D" in sys.argv:
	db = open(string_find("-D"), "r")
else:
	sys.exit("WARNING: database must be specified using '-D' flag.")

# Getting the database assembled
db_org_dictionary = {}
db_line_counter = 0
db_error_counter = 0

t0 = time.clock()

for line in db:
	if line.startswith(">") == True:
		db_line_counter += 1

		# line counter to show progress
		if db_line_counter % 1000000 == 0:							# each million
			t95 = time.clock()
			print str(db_line_counter) + " lines processed so far in " + str(t95-t0) + " seconds."

		if target_org not in line:
			continue
		else:
			splitline = line.split("  ")
			
			# ID, the hit returned in DIAMOND results
			db_id = str(splitline[0])[1:]
			
			# name and functional description
			db_entry = line.split("[", 1)
			db_entry = db_entry[0].split(" ", 1)
			db_entry = db_entry[1][1:-1]
			
			# organism name
			if line.count("[") != 1:
				splitline = line.split("[")
	
				db_org = splitline[line.count("[")].strip()[:-1]
				if db_org[0].isdigit():
					split_db_org = db_org.split()
					try:
						db_org = split_db_org[1] + " " + split_db_org[2]
					except IndexError:
						try:
							db_org = split_db_org[1]
						except IndexError:
							db_org = splitline[line.count("[")-1]
							if db_org[0].isdigit():
								split_db_org = db_org.split()
								db_org = split_db_org[1] + " " + split_db_org[2]
#							print line
#							print db_org
			else:	
				db_org = line.split("[", 1)
				db_org = db_org[1].split()
				try:
					db_org = str(db_org[1]) + " " + str(db_org[2])
				except IndexError:
					db_org = line.strip().split("[", 1)
					db_org = db_org[1][:-1]
					db_error_counter += 1
			
			db_org = re.sub('[^a-zA-Z0-9-_*. ]', '', db_org)
	
			# add to dictionaries		
			db_org_dictionary[db_id] = db_org
		
db.close()
print "Database is read and set up, moving on to the infile..."
			
infile = open (infile_name, "r")

# setting up databases
RefSeq_hit_count_db = {}
unique_seq_db = {}
line_counter = 0
hit_counter = 0

t1 = time.clock()

# reading through the infile
for line in infile:
	line_counter += 1
	splitline = line.split("\t")
	try:
		if target_org in db_org_dictionary[splitline[1]]:
			target_org_outfile.write(splitline[0] + "\t" + splitline[1] + "\t" + db_org_dictionary[splitline[1]] + "\n")
			hit_counter += 1
	except KeyError:
		continue
		
#	unique_seq_db[splitline[0]] = 1
#	try:
#		RefSeq_hit_count_db[splitline[1]] += 1
#	except KeyError:
#		RefSeq_hit_count_db[splitline[1]] = 1
#		continue
	if line_counter % 1000000 == 0:
		t99 = time.clock()
		print str(line_counter)[:-6] + "M lines processed so far in " + str(t99-t1) + " seconds."

t100 = time.clock()		
print "Run complete!"
print "Number of sequences found matching target organism, " + target_org + ": " + str(hit_counter)
print "Time elapsed: " + str(t100-t0) + " seconds."

infile.close()
target_org_outfile.close()