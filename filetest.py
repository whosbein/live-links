#!/usr/bin/env python
"""
GUH
"""

import sys, os, string

location = sys.argv[1]

file_types = set()
urls = set(['.php', '.htm', '.html'])

for root, dirs, files in os.walk(location):
    for name in files:
        filename = os.path.join(root, name) # full filename
        # name is individual file name
        ext = os.path.splitext(filename)[1]
        file_types.add(ext)
        # print extension
        path = string.replace(root, '/home/whosbein/web_dev/health/', '')
        size = os.path.getsize(filename)
        if ext in urls:
            file_type = 'url'
        else:
            file_type = 'file'

        print 'File name: %s | path: %s | size: %d | type: %s | ext: %s' % (name, path, size, file_type, ext)


#print file_types
