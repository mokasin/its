from wvtest import *
import sys
import os

sys.path.append('../')
import its

@wvtest
def test_get_keyword_dbs():
    tmp = its.get_keyword_dbs('testdata/', 'courierimapkeywords/:list')
    WVPASSEQ(len(tmp), 2)
    
    for t in tmp:
        WVPASS(os.path.isfile(t))
        WVPASSEQ(t[-len('courierimapkeywords/:list'):],\
                                                    'courierimapkeywords/:list')

@wvtest
def test_parse_courierdb():
    tmp = its.parse_courierdb('testdata/Maildir/courierimapkeywords/:list',
                             {'spam': ['junk', 'alsojunk'], 'ham': ['nonjunk']})
    print os.path.realpath('testdata/Maildir/courierimapkeywords/:list')
    WVPASSEQ(len(tmp['spam']), 4)
    WVPASSEQ(len(tmp['ham']), 1)
    WVPASS('1_mail_spam' in tmp['spam'])
    WVPASS('1_mail_spam_x' in tmp['spam'])
    WVPASS('1_mail_spam2' in tmp['spam'])
    WVPASS('1_mail_spam3' in tmp['spam'])
    WVPASS('1_mail_ham' in tmp['ham'])

@wvtest
def test_get_path_from_filename():
    tmp = its.get_path_from_filename(os.path.realpath('testdata/'),
            its.parse_courierdb('testdata/Maildir/courierimapkeywords/:list',
                            {'spam': ['junk', 'alsojunk'], 'ham': ['nonjunk']}))
    WVPASSEQ(len(tmp['spam']), 4)
    WVPASSEQ(len(tmp['ham']), 1)
    WVPASS(os.path.realpath('testdata/Maildir/mails/1_mail_spam:header') in tmp['spam'])
    WVPASS(os.path.realpath('testdata/Maildir/mails/1_mail_spam_x:xy') in tmp['spam'])
    WVPASS(os.path.realpath('testdata/Maildir/mails/1_mail_spam2:xyz') in tmp['spam'])
    WVPASS(os.path.realpath('testdata/Maildir/mails/1_mail_spam3:xyz') in tmp['spam'])

    WVPASS(os.path.realpath('testdata/Maildir/mails/1_mail_ham:random') in tmp['ham'])

@wvtest
def test_parse_mail_header():
    tmp = its.parse_mail_header('testdata/Maildir/mails/1_mail_spam:header')
    WVPASSEQ(tmp[0], 'from@me.com')
    WVPASSEQ(tmp[1], 'The subject')
