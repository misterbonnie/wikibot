#!/usr/bin/python

import optparse
import datetime
import email.utils
import wikichanges
import smtplib
import time

from email.mime.text import MIMEText

SENDER = email.utils.formataddr(('WikiBot', 'bonniek@ookpik.fnal.gov'))
RECIPIENT = email.utils.formataddr(('SLAM', 'bonniek@fnal.gov'))

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
            body = body + '\n' +  msg

        e = MIMEText(body)
        e['Subject'] = 'FEF Wiki Changes Today'
        e['From'] = 'bonniek@ookpik.fnal.gov'
        e['To'] = 'bonniek@fnal.gov'

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

    wc = wikichanges.WikiChanges(u, emit_start=True, max_age=datetime.timedelta(hours=8), gapi_key=k)

    s = WikiMail(wc)

    # threading,? NOPE
    s.mailit()
