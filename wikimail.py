#!/usr/bin/python

import optparse
import datetime
import email.utils
import wikichanges
import smtplib
import re
import time

from email.mime.text import MIMEText

SENDER = email.utils.formataddr(('WikiBot', 'bonniek@ookpik.fnal.gov'))
RECIPIENT = email.utils.formataddr(('SLAM', 'bonniek@fnal.gov'))
LIST = ''
FROM = ''

POLL_TIME = 86400

class WikiMail:
    def __init__(self, wc):
        self.last_polled = time.time()
        self.wc = wc

    def do_work(self):
        print self.last_polled, self.last_polled + POLL_TIME, time.time()
        time.sleep(POLL_TIME)
        return

    # Create a text/plain message
    def mailit(self):

        body = ''
    
        for msg in self.wc.poll():
            print msg
            msg = re.sub(r'&diff.*$', '', msg)
            msg = re.sub(r'\ [0-9].*\ ago', '', msg)
            body = body + '\n\n' +  msg

        e = MIMEText(body)
        e['Subject'] = 'FEF Wiki Changes Today'
        e['From'] = FROM
        e['To'] = LIST

        s = smtplib.SMTP('localhost')
        s.sendmail(SENDER, [RECIPIENT], e.as_string())
        s.quit()

if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('--gapi-key', dest='gapi_key', default=None,
                      help="GAPI key to use to shorten URLs. Skip it if you don't want URL shortening.")
    parser.add_option('-u', '--url', dest='url', default=None,
                      help="url.")
    (options, args) = parser.parse_args()

    k = options.gapi_key
    u = options.url

    wc = wikichanges.WikiChanges(u, emit_start=True, max_age=datetime.timedelta(hours=24), gapi_key=k)

    s = WikiMail(wc)

    # threading,? NOPE
    s.mailit()
