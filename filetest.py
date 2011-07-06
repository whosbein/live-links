#!/usr/bin/env python
"""
GUH
"""

import sys, os, string
import lxml.html as l, urllib2
from urlparse import urljoin
import re


def gen_url(in_url, current_file):
    url = ''
    http = string.replace(current_file, '/home/whosbein/web_dev/health/', \
                'http://www.austincc.edu/health/')
    url = urljoin(http, in_url)
    return url

def fix_implied_index(in_url):
    if not re.search('\.[a-zA-Z]{3}$', in_url):
        if re.search('/$', in_url):
            return in_url + 'index.php'
        else:
            return in_url + '/index.php'

    return in_url


def main():
    location = sys.argv[1]

    health_url = 'http://www.austincc.edu/health'
    #static = 'ota/' #usually just health/
    static = '' #usually just health/
    #search_url = 'http://www.austincc.edu/health/ota/'
    search_url = 'http://www.austincc.edu/health'

    #base_url needs to be acc_url + health_path + current directory in os.walk

    file_types = set()
    urls = set(['.php', '.htm', '.html'])

    for root, dirs, files in os.walk(location):
        for name in files:
            filename = os.path.join(root, name) # full filename
            # name is individual file name
            ext = os.path.splitext(filename)[1]
            #print 'root: %s ext: %s' % (root, ext)
            if ext in urls:
                file = 'file:' + filename
                print 'Links in %s' % file
                doc = l.parse(urllib2.urlopen(file))
                for link in doc.iter('a'):
                    #current_file = 
                    #print 'current_dir: %s' % current_dir
                    #print '%s: %s' % (link.text_content(), link.get('href'))
                    #print link
                    #link_target = link.find('href')
                    #print link_target
                    try:
                        link_target = link.get('href')
                        # if the link is not absolute: documents/cal.pdf etc
                        if 'http://' not in link_target:
                            link_target = gen_url(link_target, filename)
                        #print '%s: %s' % (link.text_content(), link_target)
                        #print '%s' % link.cssselect('href')
                        if search_url in link_target \
                                and '#' not in link_target \
                                and '$' not in link_target:
                            link_target = fix_implied_index(link_target)
                            print '%s' % link_target
                    except TypeError:
                        pass
                print '---------------------'

if __name__ == "__main__":
    main()
