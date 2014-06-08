from HTMLParser import HTMLParser
from urllib2 import urlopen
import urllib2
import os
import re


PAGES_DIRECTORY = "pages"
SEEN_PAGES_FILE_NAME = "pages/seen_list"

START_PAGE_REFERENCE = "http://www.kinopoisk.ru/popular/"


def html2txt(html):
    """Convert the html to raw txt """
    content = html

    p = re.compile('(<p.*?>)|(<tr.*?>)', re.I)
    t = re.compile('<td.*?>', re.I)
    comm = re.compile('<!--.*?-->', re.M)
    tags = re.compile('<.*?>', re.M)
    abbrv = re.compile('&[#\w\d]+;')

    # replace abbreviation by space
    content = abbrv.sub(' ', content)
    # remove returns time this compare to split filter join
    content = content.replace('\n', ' ')
    # replace p and tr by \n
    content = p.sub('\n', content)
    # replace td by \t
    content = t.sub('\t', content)
    # remove comments
    content = comm.sub(' ', content)
    # remove all remaining tags
    content = tags.sub(' ', content)
    # remove running spaces this remove the \n and \t
    content = re.sub('\ +', ' ', content)
    return content


class Spider(HTMLParser):
    def __init__(self, starting_url, depth, max_span, seen_pages):
        HTMLParser.__init__(self)
        self.url = starting_url
        self.db = {self.url: 1}
        self.node = [self.url]

        self.seen_pages = seen_pages

        # recursion depth max
        self.depth = depth
        # max links obtained per url
        self.max_span = max_span
        self.links_found = 0

    def handle_starttag(self, tag, attrs):
        if self.links_found < self.max_span and tag == 'a' and attrs:
            link = attrs[0][1]
            if link[:4] != "http":
                link = '/'.join(self.url.split('/')[:3])+('/'+link).replace('//', '/')

            if link not in self.db:
                print "new link ---> %s" % link
                self.links_found += 1
                self.node.append(link)
            self.db[link] = (self.db.get(link) or 0) + 1

    def crawl(self):
        for depth in xrange(self.depth):
            print "*"*70+("\nScanning depth %d web\n" % (depth+1))+"*"*70
            context_node = self.node[:]
            self.node = []
            for self.url in context_node:

                self.links_found = 0
                try:
                    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

                    req_res = urllib2.Request(self.url, headers=hdr)
                    req = urlopen(req_res)
                    encoding = req.headers.getparam('charset')

                    res = req.read().decode(encoding)
                    if self.url not in self.seen_pages:
                        self.seen_pages.add(self.url)
                        append_line(SEEN_PAGES_FILE_NAME, self.url)
                        file_name = self.url.replace("/", "@")
                        print_page_to_file(file_name, res.encode('utf8'))

                    self.feed(res)
                except urllib2.HTTPError, e:
                    print e.fp.read()
                    self.reset()

        print "*"*40 + "\nRESULTS\n" + "*"*40
        zorted = [(v, k) for (k, v) in self.db.items()]
        zorted.sort(reverse=True)
        return zorted


def read_seen_pages_list(file_name):
    seen_pages = set()
    if not os.path.isfile(file_name):
        open(file_name, "w")
        return seen_pages

    with open(file_name) as f:
        for line in f.readlines():
            seen_pages.add(line.strip())
    return seen_pages


def append_line(file_name, line):
    with open(file_name, "a") as f:
        f.write("{0}\n".format(line))


def print_page_to_file(file_name, data):
    with open("{0}/{1}".format(PAGES_DIRECTORY, file_name), "w") as f:
        f.write(html2txt(data))


def main():
    seen_pages = read_seen_pages_list(SEEN_PAGES_FILE_NAME)

    spider = Spider(starting_url=START_PAGE_REFERENCE, depth=2, max_span=100, seen_pages=seen_pages)
    result = spider.crawl()
    for (n, link) in result:
        print "%s was found %d time%s." %(link, n, "s" if n is not 1 else "")

main()