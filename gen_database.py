#!/usr/bin/env python2
"""
Methods to create and fill the database containing information about the files.
"""

import sys, os, string, sqlite3, time, re
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from urlparse import urljoin
from pprint import pprint

# This should be in a config file or something eventually
web_root = 'http://www.austincc.edu/health/ota/%s'

def gen_link_table(local_path, file_dict, c, conn):
    """
    Fills the link table in the database.
    """
    #bad_regs = [
            #re.compile(r'#'),
            #re.compile(r'^javascript'),
            #re.compile(r'^mailto')
            #]
    #absolute = re.compile(r'^http://www')
    #good_regs = [
            #re.compile(r'^http://www.austincc.edu/health/ota/')
            #]

    for root, dirs, files in os.walk(local_path):
        files = [ file for file in files \
                if file.endswith( ('.php', '.htm', '.html') ) ]
        for name in files:
            # name is individual file name
            filename = os.path.join(root, name) # full filename
            f = open(filename)
            soup = BeautifulSoup(f)
            f.close()
            for link in soup.find_all('a'):
                target = link.get('href')
                process_target(target, filename, local_path, file_dict, c, conn)
                #try:
                    #if not any(regex.match(target) for regex in bad_regs):
                        #if not absolute.match(target):
                            #target = make_link_absolute(
                                    #filename, local_path, target)
                        #if any(regex.match(target) for regex in good_regs):
                            ##print file_dict[name]
                            #insert_link(file_dict, filename,
                                    #local_path, target, c, conn)
                #except TypeError:
                    #print 'TypeError in file: %s on target link: %s' \
                            #% (filename, target)
            for link in soup.find_all('form'):
                target = link.get('action')
                process_target(target, filename, local_path, file_dict, c, conn)
                #try:
                    #if not any(regex.match(target) for regex in bad_regs):
                        #if not absolute.match(target):
                            #target = make_link_absolute(
                                    #filename, local_path, target)
                        #if any(regex.match(target) for regex in good_regs):
                            ##print file_dict[name]
                            #insert_link(file_dict, filename,
                                    #local_path, target, c, conn)
                #except TypeError:
                    #print 'TypeError in file: %s on target link: %s' \
                            #% (filename, target)

    # do custom db operations
    index_menu_fix(c, conn)

def process_target(target, filename, local_path, file_dict, c, conn):
    bad_regs = [
            re.compile(r'#'),
            re.compile(r'^javascript'),
            re.compile(r'^mailto')
            ]
    absolute = re.compile(r'^http://www')
    good_regs = [
            re.compile(r'^http://www.austincc.edu/health/ota/')
            ]

    try:
        if not any(regex.match(target) for regex in bad_regs):
            if not absolute.match(target):
                target = make_link_absolute(
                        filename, local_path, target)
            if any(regex.match(target) for regex in good_regs):
                #print file_dict[name]
                insert_link(file_dict, filename,
                        local_path, target, c, conn)
    except TypeError:
        print 'TypeError in file: %s on target link: %s' \
                % (filename, target)

def make_link_absolute(current_file, local_path, link):
    current_file = re.sub(local_path, '', current_file)
    return urljoin(web_root % current_file, link)

def insert_link(file_dict, filename, local_path, target, c, conn):
    name = re.sub(local_path, '', filename)
    try:
        #print 'source: %s dest: %s' % (file_dict[name], file_dict[target])
        c.execute("insert into link(s_id, t_id) values(?, ?)",
                (file_dict[name], file_dict[target]),)
        conn.commit()
    except KeyError:
        #print 'KeyError -- s: %s d: %s' % (name, target)
        c.execute("insert into broken(s_id, target) values(?, ?)",
                (file_dict[name], target,))
        conn.commit()

def index_menu_fix(c, conn):
    """
    Currently, the side menu is where most of the links are so using the index
    pages as the "root" doesn't do much good because it really contains no
    links.
    This method will find all index and menu files that correspond to each other
    and make a new entry in the link db that is index -> menu. This will allow
    the index file to remain a viable "root" while not needing to do any other
    fancy things.
    """

    sql = "select t1.f_id as index_id, t2.f_id as menu_id from file as t1 "\
          "join file as t2 where t1.name = 'index.php' and "\
          "t2.name = 'menu.php' and t1.depth = t2.depth and t1.path = t2.path;"
    c.execute(sql)

    results = c.fetchall()

    for row in results:
        c.execute("insert into link (s_id, t_id) values (?, ?)",
                  (row['index_id'], row['menu_id'],))

    conn.commit()

def gen_file_table(local_path, c, conn):
    """
    Fills the file table in the database.
    """

    file_types = set() # set of encountered file types
    urls = set(['.php', '.htm', '.html'])

    for root, dirs, files in os.walk(local_path):
        for name in files:
            # name is individual file name
            filename = os.path.join(root, name) # full filename
            ext = os.path.splitext(filename)[1]
            file_types.add(ext)
            path = string.replace(root, local_path, '')
            depth = 0
            if path != '':
                depth = path.count('/') + 1
            size = os.path.getsize(filename)
            last_mod = time.strftime('%Y-%m-%d %H:%M:%S',
                    time.localtime(os.path.getmtime(filename)))
            if ext in urls:
                file_type = 'url'
            else:
                file_type = 'file'

            try:
                c.execute("insert into file" \
                        "(name, depth, path, size, last_modified, type, ext) "\
                        "values (?, ?, ?, ?, ?, ?, ?)",
                        (name, depth, path, size, last_mod, file_type, ext,))
            except sqlite3.Error, e:
                print 'error on filename: %s\nError: %s' % (filename, e.args[0])
            item_id = c.lastrowid

    conn.commit()

def gen_file_dict(c, conn):
    """
    Generates a dict of full_filename -> f_id for use in quick lookups for
    link table generation.
    """
    file_dict = {}

    # Select files with a path -> rnsg/index.php and cocat
    sql = "select f_id, path || '/' || name as full_path from file "\
            "where depth != 0;"
    c.execute(sql)

    results = c.fetchall()

    for row in results:
        file_dict[row['full_path']] = row['f_id']
        file_dict[web_root % row['full_path']] = row['f_id']

    # Select files with no path -> index.php
    sql = "select f_id, name from file where depth == 0;"
    c.execute(sql)

    results = c.fetchall()

    for row in results:
        file_dict[row['name']] = row['f_id']
        file_dict[web_root % row['name']] = row['f_id']

    return file_dict

def check_for_database(db_name, c, conn):
    """
    Checks for the database and its required tables and creates them if they
    don't exist.
    """

    sql = 'create table if not exists file (f_id INTEGER PRIMARY KEY, '\
          'name TEXT, depth INT, path TEXT, live BOOLEAN DEFAULT 0, size INT, '\
          'last_modified TEXT, type TEXT, ext TEXT)'
    c.execute(sql)

    sql = 'create table if not exists link (l_id INTEGER PRIMARY KEY, '\
          's_id INTEGER, t_id INTEGER)'
    c.execute(sql)

    sql = 'create table if not exists broken (b_id INTEGER PRIMARY KEY, '\
          's_id INTEGER, target TEXT)'
    c.execute(sql)

    conn.commit()


def connect_to_database(db_name):
    """
    Checks for the database and creates it if it doesn't exist. Returns
    connection variables.
    """

    if not os.path.exists(db_name):
        print "Creating database %s" % db_name
        file = open(db_name, 'w')
        file.close()

    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    return c, conn

def main(argv=None):
    parser = ArgumentParser(description='Database creator')

    parser.add_argument('-n', '--name', action='store', dest='name',
                        required=True,
                        help='The name of the database')
    parser.add_argument('-p', '--path', action='store', dest='path',
                        required=True,
                        help='The path to the local files')
    args = parser.parse_args()

    if os.path.splitext(args.name)[1] != '.sqlite':
        args.name = args.name + '.sqlite'

    c, conn = connect_to_database(args.name)

    check_for_database(args.name, c, conn)

    gen_file_table(args.path, c, conn)

    file_dict = gen_file_dict(c, conn)
    #pprint(file_dict)

    gen_link_table(args.path, file_dict, c, conn)

if __name__ == "__main__":
    main()
