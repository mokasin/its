#!/usr/bin/env python

"""License: GPLv2
Copyright: mokasin, 2010
Only for use with Courier IMAP
"""
import os.path

import os
import getopt
import sys
import ConfigParser
import re
from  subprocess import call
from copy import deepcopy

DEFAULT_CONFIG = 'its.default.conf'
ETC_CONFIG     = '/etc/its.conf'
VERSION        = '0.1RC2'

verbose        = False
vverbose       = False


def parse_mail_header(filename):
    """It returns a tuple with (from,subject) from a given filename"""

    rex_from    = re.compile('^from: .*', re.I)
    rex_subject = re.compile('^subject: .*', re.I)

    m_from      = ''
    m_subject   = ''

    f = open(filename, 'r')
    try:
        for line in f:
            if m_from != '' and m_subject != '': break
            if rex_from.match(line) != None:
                m_from = line[6:]
            if rex_subject.match(line) != None:
                m_subject = line[9:]

    finally:
        f.close()

    #remove trailing \n
    return m_from[:-1], m_subject[:-1]

def parse_courierdb(db_fn, spham_keywords):
    """Parses a given Courier IMAP keyword database file and returns a list of\
 spam or ham mails identified by the given keyword"""

    f = open(db_fn, 'r')
    try:

        result = {'spam': [], 'ham': []}
        kw_indeces = dict()

        n = 0
        line = f.readline()

        while line != '\n':
            #find spam/ham index --> [:-1] to snip trailing \n
            if line[:-1] in spham_keywords.keys():
                kw_indeces[spham_keywords[line[:-1]]] = str(n)
            n += 1
            line = f.readline()

        #find mails tagged as spam/ham
        for line in f:
            #indeces of keywords the mail is marked with
            tmp = line.split(':')[1].split()

            #if there are marked spam AND ham mails
            if len(kw_indeces) == 2:
                #if the mail is marked as spam AND ham, don't know which to
                #prefere, so continue
                if kw_indeces['spam'] in tmp and kw_indeces['ham'] in tmp:
                    continue

            #key is one of 'spam', 'ham'
            for key in kw_indeces:
                if kw_indeces[key] in tmp:
                    #append mailname to spam or ham result list
                    result[key].append(line.split(':')[0])

        return result

    finally:
        f.close()



def get_path_from_filename(path, spam_ham_dict):
    """Looking for a file in path"""

    result = {'spam':[], 'ham':[]}

    spam_ham_dict_copy = deepcopy(spam_ham_dict)

    for root, dirs, files in os.walk(path):
        for file in files:
            #key has values: spam, ham
            for key in spam_ham_dict:
                try:
                    #if the filename was found
                    index = spam_ham_dict_copy[key].index(file.split(':')[0])

                    #add it to result and kick out the associated mail name
                    result[key].append(os.path.realpath(
                                                    os.path.join(root, file)))
                    del spam_ham_dict_copy[key][index]
                except:
                    #just continue if ValueError is raised, because the mail
                    #isn't found by index or any other error occured
                    continue

    return result


def get_keyword_dbs(path, db_dirname_scheme):
    """crawls path and all subdirectories for imap keywords"""

    result = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.join(root,file)[-len(db_dirname_scheme):] ==\
                                                            db_dirname_scheme:
                    result.append(os.path.join(root,file))

    return result


def teach_spamassassin(spham_filenames, sa_learn_path):
    """calls sa-learn to teach spamassissin"""
    try:
        for key in spham_filenames:
            for file in spham_filenames[key]:
                    if call([sa_learn_path, '--' + key, file]) != 0:
                        print "ERROR calling" + sa_learn_path + \
                        ". Something went wrong."
                        sys.exit(1)
                    elif verbose and not vverbose:
                        print "   --> teached " + key + ": ..." + file[-40:]
                    elif verbose and vverbose:
                        m_from, m_subject = parse_mail_header(file)
                        print "   --> teached " + key + ": ..." + file[-30:] + \
                            " | FROM: " + m_from + ' | SUBJECT: ' + m_subject
    except OSError:
        print "ERROR: Couldn't call" + sa_learn_path +\
                                                ". Perhaps it doesn't exist?"
        sys.exit(1)




def usage():
    """prints out the usage options"""

    s = sys.stdout

    s.write(
"""IMAP's Teaching Spamassassin v{version} Copyright 2010 mokasin GPLv2

USAGE
its.py [-c configfile|--config configfile] [-v] [-h|--help] path

    -h                This help
    --help
    -c configfile     give path to config file other than '{etc_config}'
    -v                be verbose

WHAT IT DOES
This script crawls 'path' for a CourierIMAP keyword database. The database's
filename is found using the 'keyword_dirname_scheme'. It searches for IMAP key-
words defined in the configfile ('spam_keyword', 'ham_keyword') to find flagged
spam or ham mails and finally give them to sa-learn to teach Spamassassin.

CONFIGFILE

Look at 'its.default.config' for a commented version with presettings for
Thunderbird.
""".format(version=VERSION, etc_config=ETC_CONFIG))




def main():
    """The main function"""

    global verbose
    global vverbose

    configfile = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:v', ['help','config'])

        if len(args) != 1:
            print "Please give (only) one path to act on."
            usage()
            sys.exit(2)
        elif not os.path.exists(args[0]):
            print "ERORR: Given path doesn't exist."
            sys.exit(1)

    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for optlist, arguments in opts:
        if optlist == '-v':
            vverbose = verbose
            verbose = True
        elif optlist in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif optlist in ('-c', '--config'):
            configfile = arguments
        else:
            assert False, 'unhandled option'

    # now the action
    
    config = ConfigParser.RawConfigParser()
    if config.read([ETC_CONFIG, configfile]) == []:
        print("Please specify a configuration file. Copy 'its.default.conf'"
                    "to '/etc/its.conf' or specify your own using the '-c'")
        usage()
        sys.exit(2)


    try:

        for db in get_keyword_dbs(args[0], config.get('mailserver',
                                          'keyword_dirname_scheme')):

            if verbose:
                print "\nFound DB:  " + db

            tagged_mailes = parse_courierdb(db,
                              {config.get('mailclient', 'spam_keyword'): 'spam',
                               config.get('mailclient', 'ham_keyword'): 'ham'})

            try:
                #crawl only maildir where the db was found
                #it' uneccessary to crawl every path
                path = db[:db.index(config.get('mailserver','maildir_scheme'))\
                            + len(config.get('mailserver', 'maildir_scheme'))]
                if verbose:
                    print "Looking in " + path + " for tagged mails."
            except ValueError:
                path = args[0]

            spham_filenames = get_path_from_filename(path, tagged_mailes)

            if verbose:
                print "  --> Found %d spam and %d ham mails" % \
               (len(spham_filenames['spam']), len(spham_filenames['ham']))

            if (verbose and \
                   (len(spham_filenames['spam']) > 0 \
                or  len(spham_filenames['ham']) > 0 )):
                print "\nNow the teaching beginns...\n"

            teach_spamassassin(spham_filenames, config.get('spamassassin',
                                                            'sa_learn_path'))
            if verbose:
                print '-'*80


    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        print "ERROR: Configfile ist corrupt. Please check it and look at\
 'its.default.conf'"
        sys.exit(1)



if __name__ == '__main__':
    main()
