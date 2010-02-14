#!/usr/bin/env python

import os
import getopt, sys

#TODO make config file

sa_learn_path = '/usr/bin/sa-learn'

g_spam_keyword = 'Junk'
g_ham_keyword = 'nonjunk'

keyword_dirname_pattern = 'courierimapkeywords/:list'


def parse_courierdb(db_fn, spam_keyword, ham_keyword):
	"""Parses a given Courier IMAP keyword database file and returns a list of
		spam or ham mails identified by the given keyword"""

	f = open(db_fn, 'r')
	try:

		result = dict( [ ('spam', []), ('ham', []) ] )
		keywords = dict()
		n = 0
		line = f.readline()

		while line != '\n':
			keywords[line[:-1]] = str(n)
			n += 1
			line = f.readline()

		for line in f:
			for index in line.split(':')[1].split():
				if index == keywords.get(spam_keyword, '-1'):
					result['spam'].append(line[:-1].split(':')[0])

				elif index == keywords.get(ham_keyword, '-1'):
					result['ham'].append(line[:-1].split(':')[0])
	
		return result

	finally:
		f.close()


def get_path_from_filename(path, filenames):
	"""Looking for a file in path"""
	result = []

	for filename in filenames:
		for root, dirs, files in os.walk(path):
			for file in files:
				if file.split(':')[0] == filename:
					result.append(os.path.join(root, file))

	return result


def get_keyword_dbs(path):
	"""crawls path and all subdirectories for imap keywords"""

	result = []

	for root, dirs, files in os.walk(path):
		for file in files:
			for i in range(1, len(keyword_dirname_pattern.split('/'))):
				if os.path.join(root,file).split('/')[-i] == keyword_dirname_pattern.split('/')[-i]:
					result.append(os.path.join(root,file))

	return result


def teach_spamassassin(filenames, spam=True):
	"""calls sa-learn to teach spamassissin"""

	#TODO Implement this functionality

	if spam:
		print "Now comes the spam:"
	else:
		print "Now comes the ham:"

	print filenames


def usage():
	"""prints out the usage options"""

	print 'TODO: How to use'



def main():
	"""The main function"""

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'h:v', ['help'])

		if len(args) > 1:
			print "Please give only one path."
			usage()
			sys.exit()

	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	verbose = False
	for optlist, arguments in opts:
		if optlist == '-v':
			verbose = True
		elif optlist in ('-h', '--help'):
			usage()
			sys.exit()
		else:
			assert False, 'unhandled option'

	# now the action

	spam = []
	ham = []

	for db in  get_keyword_dbs(args[0]):
		tagged_mailes = parse_courierdb(db, g_spam_keyword, g_ham_keyword)

		spam.extend(get_path_from_filename(args[0], tagged_mailes['spam']))
		ham.extend(get_path_from_filename(args[0], tagged_mailes['ham']))

	teach_spamassassin(spam)
	teach_spamassassin(ham, False)



if __name__ == '__main__':
	main()