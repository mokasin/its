from wvtest import *
import sys
import os

sys.path.append('../')
import its

@wvtest
def test_get_keyword_dbs():
    tmp = its.get_keyword_dbs('testdata/', 'courierimapkeywords/:list')
    WVPASSEQ(len(tmp), 3)
    
    for t in tmp:
        WVPASS(os.path.isfile(t))
        WVPASSEQ(t.split('/')[-1:], [':list'])

@wvtest
def test_parse_courierdb():
    tmp = its.parse_courierdb('testdata/1/Maildir/courierimapkeywords/:list',
                                            {'Junk': 'spam', 'nonjunk': 'ham'})
    WVPASSEQ(len(tmp['spam']), 2)
    WVPASSEQ(len(tmp['ham']), 1)
    WVPASS('1_mail_spam' in tmp['spam'])
    WVPASS('1_mail_spam_x' in tmp['spam'])
    WVPASS('1_mail_ham' in tmp['ham'])

@wvtest
def test_get_path_from_filename():
    tmp = its.get_path_from_filename(os.path.realpath('testdata/1'),
            its.parse_courierdb('testdata/1/Maildir/courierimapkeywords/:list',
                                            {'Junk': 'spam', 'nonjunk': 'ham'}))
    WVPASSEQ(len(tmp['spam']), 2)
    WVPASSEQ(len(tmp['ham']), 1)
    WVPASS(os.path.realpath('testdata/1/Maildir/mails/1_mail_spam:header') in tmp['spam'])
    WVPASS(os.path.realpath('testdata/1/Maildir/mails/1_mail_spam_x:xy') in tmp['spam'])
    WVPASS(os.path.realpath('testdata/1/Maildir/mails/1_mail_ham:random') in tmp['ham'])

@wvtest
def test_parse_mail_header():
    tmp = its.parse_mail_header('testdata/1/Maildir/mails/1_mail_spam:header')
    WVPASSEQ(tmp[0], 'from@me.com')
    WVPASSEQ(tmp[1], 'The subject')
