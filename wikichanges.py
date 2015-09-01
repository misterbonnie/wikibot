import sys
import time
import xmltodict
import requests
import isodate
import pytz
import datetime
import json


class WikiChanges(object):

    def __init__(self, url, emit_start=False, max_age=None, gapi_key=None):
        self.url = url
        self.synced = False
        self.messages = set()
        self.emit_start = emit_start
        self.max_age = max_age
        self.key = gapi_key

    def shorten(self, url):
        if not self.key:
            return url

        try :
            shorten_url = 'https://www.googleapis.com/urlshortener/v1/url'
            qs = '?key=' + self.key
            headers = {'content-type': 'application/json'}
            data = json.dumps({'longUrl': url})
            res = requests.post(shorten_url + qs, data=data, headers=headers).text
            return json.loads(res)['id']
        except :
            # it's url shortening. what do you want? I'm sorry that I'm not syslogging this. So very sorry.
            # I lied, I'm not sorry.
            return url

    def poll(self):
        already_have = []
        r = requests.get(self.url, verify=False)
        d = xmltodict.parse(r.text)
        entries = d['feed']['entry']
        entries.reverse()
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc, microsecond=0)
        print entries
        for e in entries:
            url = e['link']['@href']
            name = e['author']['name']
            title = e['title']
            updated = isodate.parse_datetime(e['updated'])
            age = now - updated
            if url not in self.messages:
                age_str = 'just now'
                if age > datetime.timedelta(minutes=3):
                    age_str = '%s ago' % str(age)
                msg = '%s edited "%s" %s %s' % (name, title, age_str, self.shorten(url))
                self.messages.add(url)
                if self.synced or self.emit_start:
                    if self.max_age is not None:
                        if age > self.max_age:
                            continue
                    if (e['title'], e['author']['name']) not in already_have:
                        # for my thing i just want the pages not the diffs
                        already_have.append((e['title'], e['author']['name']))
                        yield msg
        self.synced = True

if __name__ == '__main__':
    wc = WikiChanges(sys.argv[1], emit_start=True, max_age=datetime.timedelta(hours=24))
    while True:
        for msg in wc.poll():
            print msg
        time.sleep(60)
